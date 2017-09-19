import cgi
import dateparser
import datetime
import logging
import re
import urlparse

from dancedeets import fb_api
from mapreduce import context
from mapreduce import control
from mapreduce import operation

from dancedeets.users import users
from dancedeets.util import deferred
from dancedeets.util import fb_mapreduce
from . import event_pipeline
from . import potential_events
from . import thing_db


def delete_bad_source(source):
    if source.creating_fb_uid or source.num_real_events:
        if source.street_dance_related != True:
            source.street_dance_related = True
            yield operation.db.Put(source)
        yield '+%s\n' % source.graph_id
    elif source.num_potential_events:
        if source.street_dance_related != False:
            source.street_dance_related = False
            yield operation.db.Put(source)
        yield ' %s\n' % source.graph_id
    else:
        sid = source.graph_id
        yield operation.db.Delete(source)
        yield '-%s\n' % sid


def mr_delete_bad_sources():
    mapper_params = {
        'entity_kind': 'dancedeets.event_scraper.thing_db.Source',
        'output_writer': {
            'mime_type': 'text/plain',
            'bucket_name': 'dancedeets-hrd.appspot.com',
        },
    }
    control.start_map(
        name='Delete Bad Sources',
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec='dancedeets.event_scraper.thing_scraper.delete_bad_source',
        output_writer_spec='mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        shard_count=8,
        queue_name='fast-queue',
        mapper_parameters=mapper_params,
    )


def scrape_events_from_sources(fbl, sources):
    fbl.allow_cache = False
    discovered_list = discover_events_from_sources(fbl, sources)
    fbl.allow_cache = True
    process_event_source_ids(discovered_list, fbl)


def discover_events_from_sources(fbl, sources):
    ctx = context.get()
    if ctx:
        params = ctx.mapreduce_spec.mapper.params
        min_potential_events = params.get('min_potential_events', 0)
        sources = [x for x in sources if min_potential_events <= (x.num_potential_events or 0)]

    # Maybe we can build this into the upfront mapreduce filter?
    # Unfortunately, '!='' is more difficult to do and requires better schema planning,
    # so let's just do this for now.
    # Hopefully this also prevents the API Rate limits on GET {user-id} lookups.
    sources = [x for x in sources if x.graph_type != thing_db.GRAPH_TYPE_PROFILE]

    # don't scrape sources that prove useless and give mostly garbage events
    #sources = [x for x in sources if x.fraction_potential_are_real() > 0.05]

    if fbl.allow_cache:
        logging.error('discover_events_from_sources unexpectedly called with a disabled cache!')

    logging.info("Looking up sources: %s", [x.graph_id for x in sources])
    fbl.request_multi(fb_api.LookupThingCommon, [x.graph_id for x in sources])
    # Now based on the sources we know, grab the appropriate fb data
    for s in sources:
        fbl.request(thing_db.get_lookup_for_graph_type(s.graph_type), s.graph_id)
    fbl.batch_fetch()

    logging.info("Fetched %s URLs, saved %s updates", fbl.fb_fetches, fbl.db_updates)

    discovered_list = set()
    for source in sources:
        try:
            discovered_list.update(_process_thing_feed(fbl, source))
        except fb_api.NoFetchedDataException, e:
            logging.warning("Failed to fetch data for thing: %s", str(e))
    logging.info("Discovered %s items: %s", len(discovered_list), discovered_list)
    return discovered_list


def scrape_events_from_source_ids(fbl, source_ids):
    sources = thing_db.Source.get_by_key_name(source_ids)
    sources = [x for x in sources if x]
    logging.info("Looking up %s source_ids, found %s sources", len(source_ids), len(sources))
    scrape_events_from_sources(fbl, sources)


map_scrape_events_from_sources = fb_mapreduce.mr_wrap(scrape_events_from_sources)


def mapreduce_scrape_all_sources(fbl, min_potential_events=None, queue='slow-queue'):
    # Do not do the min_potential_events>1 filter in the mapreduce filter,
    # or it will want to do a range-shard on that property. Instead, pass-it-down
    # and use it as an early-return in the per-Source processing.
    # TODO:....maybe we do want a range-shard filter? save on loading all the useless sources...
    fb_mapreduce.start_map(
        fbl,
        'Scrape All Sources',
        'dancedeets.event_scraper.thing_scraper.map_scrape_events_from_sources',
        'dancedeets.event_scraper.thing_db.Source',
        handle_batch_size=10,
        extra_mapper_params={'min_potential_events': min_potential_events},
        queue=queue,
        randomize_tokens=True,
    )


def mapreduce_create_sources_from_events(fbl):
    fb_mapreduce.start_map(
        fbl,
        'Create Sources from Events',
        'dancedeets.event_scraper.thing_db.map_create_sources_from_event',
        'dancedeets.events.eventdata.DBEvent',
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


def _process_thing_feed(fbl, source):
    fb_source_common = fbl.fetched_data(fb_api.LookupThingCommon, source.graph_id)
    if source.creation_time is None:
        source.creation_time = datetime.datetime(2010, 1, 1)
        source.put()

    if fb_source_common['empty']:
        logging.warning("Source %s was empty: %s", source.graph_id, fb_source_common['empty'])
        return []
    # TODO(lambert): do we really need to scrape the 'info' to get the id, or we can we half the number of calls by just getting the feed? should we trust that the type-of-the-thing-is-legit for all time, which is one case we use 'info'?
    if 'data' not in fb_source_common['feed']:
        logging.error("No 'data' found in: %s", fb_source_common['feed'])
        return []

    # In case any of our MR's failed and updated the last_scrape_time prematurely,
    # we still want to check back and make sure we include them.
    # Setting a high-watermark means the map produces 50K (new) events instead of 500K (old+new) events.
    if source.last_scrape_time:
        post_high_watermark = source.last_scrape_time - datetime.timedelta(days=2)
    else:
        post_high_watermark = datetime.datetime.min

    logging.info('Finding events on source %s, using high watermark %s', source.graph_id, post_high_watermark)
    fb_source_data = fbl.fetched_data(thing_db.get_lookup_for_graph_type(source.graph_type), source.graph_id)
    source.compute_derived_properties(fb_source_common, fb_source_data)
    # save new name, feed_history_in_seconds
    source.last_scrape_time = datetime.datetime.now()
    source.put()

    discovered_list = build_discovered_from_feed(source, fb_source_common['feed']['data'], post_high_watermark)

    # Now also grab the events that the page owns/manages itself:
    for event in fb_source_common['events']['data']:
        updated_time = dateparser.parse(event['updated_time'])
        if post_high_watermark < updated_time:
            discovered = potential_events.DiscoveredEvent(event['id'], source, thing_db.FIELD_FEED)
            discovered_list.append(discovered)
    return discovered_list


def build_discovered_from_feed(source, feed_data, post_high_watermark):
    discovered_list = []
    for post in feed_data:
        links = []
        p = None
        if 'link' in post:
            link = post['link']
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
                if source and source.graph_id == extra_source_id:
                    extra_source_id = None
                updated_time = dateparser.parse(post['updated_time'])
                if post_high_watermark < updated_time:
                    discovered = potential_events.DiscoveredEvent(eid, source, thing_db.FIELD_FEED, extra_source_id)
                    discovered_list.append(discovered)
            else:
                logging.warning("broken link is %s", urlparse.urlunparse(p))
    return discovered_list


def process_event_source_ids(discovered_list, fbl):
    # TODO(lambert): maybe trim any ids from posts with dates "past" the last time we scraped? tricky to get correct though
    logging.info("Loading processing %s discovered events", len(discovered_list))
    event_pipeline.process_discovered_events(fbl, discovered_list)

    # TODO: Should only run this code on events that we actually decide are worth adding
    if False:
        potential_new_source_ids = set([x.extra_source_id for x in discovered_list if x.extra_source_id])
        existing_source_ids = set([x.graph_id for x in thing_db.Source.get_by_key_name(potential_new_source_ids) if x])
        new_source_ids = set([x for x in potential_new_source_ids if x not in existing_source_ids])
        for source_id in new_source_ids:
            #TODO(lambert): we know it doesn't exist, why does create_source_from_id check datastore?
            s = thing_db.Source(key_name=source_id)
            s.put()
        logging.info("Found %s new sources", len(new_source_ids))

        # initiate an out-of-band-scrape for our new sources we found
        if new_source_ids:
            deferred.defer(scrape_events_from_source_ids, fbl, new_source_ids)


def scrape_events_from_source_ids_with_fallback(fbl, source_ids):
    for source_id in source_ids:
        try:
            scrape_events_from_source_ids(fbl, [source_id])
        except fb_api.ExpiredOAuthToken:
            logging.warning("Found ExpiredOAuthtoken %s when scraping source, falling back to main token: %s", fbl, source_id)
            user = users.User.get_by_id('701004')
            fbl = user.get_fblookup()
            scrape_events_from_source_ids(fbl, [source_id])
