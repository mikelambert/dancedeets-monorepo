import cgi
import datetime
import logging
import re
import urlparse

from google.appengine.ext import deferred

import fb_api
from mapreduce import context
from util import fb_mapreduce
from util import timings
from . import potential_events
from . import thing_db


def delete_bad_source(source):
    if source.creating_fb_uid or source.num_real_events:
        if source.street_dance_related != True:
            source.street_dance_related = True
            source.put()
        yield '+%s\n' % source.graph_id
    elif source.num_potential_events:
        if source.street_dance_related != False:
            source.street_dance_related = False
            source.put()
        yield ' %s\n' % source.graph_id
    else:
        sid = source.graph_id
        source.delete()
        yield '-%s\n' % sid

def mr_delete_bad_sources():
    mapper_params = {
        'entity_kind': 'event_scraper.thing_db.Source',
        'output_writer': {
            'mime_type': 'text/plain',
            'bucket_name': 'dancedeets-hrd.appspot.com',
        },
    }
    from mapreduce import control
    control.start_map(
        name='Delete Bad Sources',
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec='event_scraper.thing_scraper.delete_bad_source',
        output_writer_spec='mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        shard_count=8, # since we want to stick it in the slow-queue, and don't care how fast it executes
        queue_name='fast-queue',
        mapper_parameters=mapper_params,
    )


@timings.timed
def scrape_events_from_sources(fbl, sources):
    ctx = context.get()
    if ctx:
        params = ctx.mapreduce_spec.mapper.params
        min_potential_events = params.get('min_potential_events', 0)
        sources = [x for x in sources if min_potential_events <= x.num_potential_events]

    # don't scrape sources that prove useless and give mostly garbage events
    #sources = [x for x in sources if x.fraction_potential_are_real() > 0.05]

    logging.info("Looking up sources: %s", [x.graph_id for x in sources])
    fbl.request_multi(fb_api.LookupThingFeed, [x.graph_id for x in sources])
    fbl.batch_fetch()

    logging.info("Fetched %s URLs, saved %s updates", fbl.fb_fetches, fbl.db_updates)

    discovered_list = set()
    for source in sources:
        try:
            thing_feed = fbl.fetched_data(fb_api.LookupThingFeed, source.graph_id)
            discovered_list.update(process_thing_feed(source, thing_feed))
        except fb_api.NoFetchedDataException, e:
            logging.error("Failed to fetch data for thing: %s", str(e))
    logging.info("Discovered %s items: %s", len(discovered_list), discovered_list)
    process_event_source_ids(discovered_list, fbl)

def scrape_events_from_source_ids(fbl, source_ids):
    sources = thing_db.Source.get_by_key_name(source_ids)
    scrape_events_from_sources(fbl, sources)

map_scrape_events_from_source = fb_mapreduce.mr_wrap(scrape_events_from_sources)

def mapreduce_scrape_all_sources(fbl, min_potential_events=None, queue='super-slow-queue'):
    # Do not do the min_potential_events>1 filter in the mapreduce filter,
    # or it will want to do a range-shard on that property. Instead, pass-it-down
    # and use it as an early-return in the per-Source processing.
    fb_mapreduce.start_map(
        fbl,
        'Scrape All Sources',
        'event_scraper.thing_scraper.map_scrape_events_from_source',
        'event_scraper.thing_db.Source',
        handle_batch_size=10,
        output_writer={'min_potential_events': min_potential_events},
        queue=queue,
    )

def mapreduce_create_sources_from_events(fbl):
    fb_mapreduce.start_map(
        fbl,
        'Create Sources from Events',
        'event_scraper.thing_db.map_create_source_from_event',
        'events.eventdata.DBEvent',
    )

def parsed_event_link(url):
    p = urlparse.urlparse(url)
    # allow relative urls
    good_domain = p.netloc in ['', 'www.facebook.com', 'm.facebook.com']
    if p.fragment.startswith('!/'):
        return parsed_event_link(urlparse.urljoin(url, p.fragment[1:]))
    good_path = p.path == '/event.php' or p.path.startswith('/events/')
    if good_domain and good_path:
        return p
    else:
        return None

def process_thing_feed(source, thing_feed):
    if thing_feed['empty']:
        logging.warning("Source %s was empty: %s", source.graph_id, thing_feed['empty'])
        return []
    # TODO(lambert): do we really need to scrape the 'info' to get the id, or we can we half the number of calls by just getting the feed? should we trust that the type-of-the-thing-is-legit for all time, which is one case we use 'info'?
    if 'data' not in thing_feed['feed']:
        logging.error("No 'data' found in: %s", thing_feed['feed'])
        return []
    
    # save new name, feed_history_in_seconds
    source.compute_derived_properties(thing_feed)
    source.last_scrape_time = datetime.datetime.now()
    source.put()

    discovered_list = build_discovered_from_feed(source, thing_feed['feed']['data'])

    # Now also grab the events that the page owns/manages itself:
    for event in thing_feed['events']['data']:
        discovered = potential_events.DiscoveredEvent(event['id'], source, thing_db.FIELD_FEED)
        discovered_list.append(discovered)
    return discovered_list

def build_discovered_from_feed(source, feed_data):
    discovered_list = []
    for post in feed_data:
        links = []
        p = None
        if 'link' in post:
            link = post['link']
            links.append(link)
        # sometimes 'pages' have events-created, but posted as status messages that we need to parse out manually
        for x in post.get('actions', []):
            link = x['link']
            links.append(link)
        if post.get('message'):
            links.extend(re.findall("https?://[A-Za-z0-9-._~:/?#@!$&\'()*+,;=%]+", post.get('message')))
        links = [x for x in links if x]
        # Now go over the links in this particular post, grabbing anything we need
        for p in links:
            p = parsed_event_link(p)
            if not p:
                continue
            qs = cgi.parse_qs(p.query)
            if 'eid' in qs:
                eid = qs['eid'][0]
            eid = None
            if p.path.startswith('/events/'):
                potential_eid = p.path.split('/')[2]
                m = re.match(r'(\d+)', potential_eid)
                if m:
                    eid = m.group(1)
            if eid:
                extra_source_id = post['from']['id']
                discovered = potential_events.DiscoveredEvent(eid, source, thing_db.FIELD_FEED, extra_source_id)
                discovered_list.append(discovered)
            else:
                logging.warning("broken link is %s", urlparse.urlunparse(p))
    return discovered_list

def process_event_source_ids(discovered_list, fbl):
    # TODO(lambert): maybe trim any ids from posts with dates "past" the last time we scraped? tricky to get correct though
    logging.info("Loading data for %s events", len(discovered_list))
    potential_new_source_ids = set()
    for discovered in discovered_list:
        fbl.request(fb_api.LookupEvent, discovered.event_id)
        #DISABLE_ATTENDING
        #fbl.request(fb_api.LookupEventAttending, discovered.event_id)
        potential_new_source_ids.add(discovered.extra_source_id)
    fbl.batch_fetch()

    logging.info("Going to process fetched events and construct potential events:")
    # TODO(lambert): Maybe filter this event out for itself and its sources, before we attempt to load event-attending and recreate it?
    # TODO(lambert): like what we do with potential-events-from-invites? maybe combine those flows?
    for discovered in discovered_list:
        logging.info("Processing event id %s", discovered.event_id)
        try:
            fb_event = fbl.fetched_data(fb_api.LookupEvent, discovered.event_id)
            if fb_event['empty']:
                continue
            discovered = potential_events.DiscoveredEvent(discovered.event_id, discovered.source, discovered.source_type)
            potential_events.make_potential_event_with_source(fb_event, discovered)
        except fb_api.NoFetchedDataException:
            continue
    logging.info("Found %s potential events", len(discovered_list))

    existing_source_ids = set([x.graph_id for x in thing_db.Source.get_by_key_name(potential_new_source_ids) if x])
    new_source_ids = set([x for x in potential_new_source_ids if x not in existing_source_ids])
    for source_id in new_source_ids:
        #TODO(lambert): we know it doesn't exist, why does create_source_for_id check datastore?
        s = thing_db.Source(key_name=source_id)
        s.put()
    logging.info("Found %s new sources", len(new_source_ids))

    # initiate an out-of-band-scrape for our new sources we found
    if new_source_ids:
        deferred.defer(scrape_events_from_source_ids, fbl, new_source_ids)

