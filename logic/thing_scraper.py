import cgi
import datetime
import logging
import re
import urlparse

from google.appengine.ext import deferred

import fb_api
from logic import potential_events
from logic import thing_db

from util import fb_mapreduce
from util import timings

@timings.timed
def scrape_events_from_sources(batch_lookup, sources):
    # don't scrape sources that prove useless and give mostly garbage events
    sources = [x for x in sources if x.fraction_potential_are_real() > 0.05]

    batch_lookup = batch_lookup.copy(allow_cache=False)
    for source in sources:
        batch_lookup.lookup_thing_feed(source.graph_id)
    batch_lookup.finish_loading()

    logging.info("Fetched %s objects, saved %s updates", batch_lookup.fb_fetches, batch_lookup.db_updates)

    event_source_combos = []
    for source in sources:
        try:
            thing_feed = batch_lookup.data_for_thing_feed(source.graph_id)
            event_source_combos.extend(process_thing_feed(source, thing_feed))
        except fb_api.NoFetchedDataException, e:
            logging.error("Failed to fetch data for thing: %s", str(e))

    process_event_source_ids(event_source_combos, batch_lookup.copy(allow_cache=True))

def scrape_events_from_source_ids(batch_lookup, source_ids):
    sources = thing_db.Source.get_by_key_name(source_ids)
    scrape_events_from_sources(batch_lookup, sources)

map_scrape_events_from_source = fb_mapreduce.mr_wrap(scrape_events_from_sources)

def mapreduce_scrape_all_sources(batch_lookup, min_potential_events=None):
    filters = []
    if min_potential_events:
        filters.append(('num_potential_events', '>=', min_potential_events))
    fb_mapreduce.start_map(
        batch_lookup.copy(allow_cache=False), # Force refresh of thing feeds
        'Scrape All Sources',
        'logic.thing_scraper.map_scrape_events_from_source',
        'logic.thing_db.Source',
        handle_batch_size=10,
        filters=filters,
        queue='super-slow-queue',
    )

def mapreduce_create_sources_from_events(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup,
        'Create Sources from Events',
        'logic.thing_db.map_create_source_from_event',
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
        return []
    # TODO(lambert): do we really need to scrape the 'info' to get the id, or we can we half the number of calls by just getting the feed? should we trust that the type-of-the-thing-is-legit for all time, which is one case we use 'info'?
    if 'data' not in thing_feed['feed']:
        logging.error("No 'data' found in: %s", thing_feed['feed'])
        return []
    
    # save new name, feed_history_in_seconds
    source.compute_derived_properties(thing_feed)
    source.last_scrape_time = datetime.datetime.now()
    source.put()

    event_source_combos = parse_event_source_combos_from_feed(source, thing_feed['feed']['data'])
    return event_source_combos

def parse_event_source_combos_from_feed(source, feed_data):
    event_source_combos = []
    for post in feed_data:
        p = None
        if 'link' in post:
            link = post['link']
            p = parsed_event_link(link)
        else:
            # sometimes 'pages' have events-created, but posted as status messages that we need to parse out manually
            for x in post.get('actions', []):
                link = x['link']
                p = parsed_event_link(link)
                if p:
                    break
        if p:
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
                extra_source_id = None
                if 'from' in post:
                    extra_source_id = post['from']['id']
                event_source_combos.append((eid, source, extra_source_id))
            else:
                logging.error("broken link is %s", urlparse.urlunparse(p))
    return event_source_combos

def process_event_source_ids(event_source_combos, batch_lookup):
    # TODO(lambert): maybe trim any ids from posts with dates "past" the last time we scraped? tricky to get correct though
    potential_new_source_ids = set()
    for event_id, source, posting_source_id in event_source_combos:
        batch_lookup.lookup_event(event_id)
        batch_lookup.lookup_event_attending(event_id)
        potential_new_source_ids.add(posting_source_id)
    batch_lookup.finish_loading()

    # TODO(lambert): Maybe filter this event out for itself and its sources, before we attempt to load event-attending and recreate it?
    # TODO(lambert): like what we do with potential-events-from-invites? maybe combine those flows?
    for event_id, source, posting_source_id in event_source_combos:
        try:
            fb_event = batch_lookup.data_for_event(event_id)
            fb_event_attending = batch_lookup.data_for_event_attending(event_id)
            if fb_event['empty']:
                continue
            potential_events.make_potential_event_with_source(event_id, fb_event, fb_event_attending, source=source, source_field=thing_db.FIELD_FEED)
        except fb_api.NoFetchedDataException:
            continue
    logging.info("Found %s potential events", len(event_source_combos))

    existing_source_ids = set([str(x.graph_id) for x in thing_db.Source.get_by_key_name(potential_new_source_ids) if x])
    new_source_ids = set([x for x in potential_new_source_ids if x not in existing_source_ids])
    for source_id in new_source_ids:
        #TODO(lambert): we know it doesn't exist, why does create_source_for_id check datastore?
        s = thing_db.Source(key_name=str(source_id))
        s.put()
    logging.info("Found %s new sources", len(new_source_ids))

    # initiate an out-of-band-scrape for our new sources we found
    if new_source_ids:
        deferred.defer(scrape_events_from_source_ids, batch_lookup.copy(), new_source_ids)

