import cgi
import datetime
import logging
import urlparse

import facebook

from google.appengine.ext import deferred

from events import eventdata
import fb_api
from logic import event_classifier
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

def mapreduce_scrape_all_sources(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup.copy(allow_cache=False), # Force refresh of thing feeds
        'Scrape All Sources',
        'logic.thing_scraper.map_scrape_events_from_source',
        'logic.thing_db.Source',
        handle_batch_size=10,
    )

def mapreduce_create_sources_from_events(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup,
        'Create Sources from Events',
        'logic.thing_db.map_create_source_from_event',
        'events.eventdata.DBEvent',
    )

def process_thing_feed(source, thing_feed):
    if thing_feed['deleted']:
        return []
    # TODO(lambert): do we really need to scrape the 'info' to get the id, or we can we half the number of calls by just getting the feed? should we trust that the type-of-the-thing-is-legit for all time, which is one case we use 'info'?
    if 'data' not in thing_feed['feed']:
        logging.error("No 'data' found in: %s", thing_feed['feed'])
        return []
    
    # save new name, feed_history_in_seconds
    source.compute_derived_properties(thing_feed)
    source.last_scrape_time = datetime.datetime.now()
    source.put()

    event_source_combos = []
    for post in thing_feed['feed']['data']:
        if 'link' in post:
            p = urlparse.urlparse(post['link'])
            if p.netloc == 'www.facebook.com' and (p.path == '/event.php' or p.path.startswith('/events/')):
                event_id = None
                qs = cgi.parse_qs(p.query)
                if 'eid' in qs:
                    eid = qs['eid'][0]
                if p.path.startswith('/events/'):
                    eid = p.path.split('/')[2]
                if eid:
                    extra_source_id = None
                    if 'from' in post:
                        extra_source_id = post['from']['id']
                    event_source_combos.append((eid, source, extra_source_id))
                else:
                    logging.error("broken link is %s", post['link'])
    return event_source_combos

def process_event_source_ids(event_source_combos, batch_lookup):
    # TODO(lambert): maybe trim any ids from posts with dates "past" the last time we scraped? tricky to get correct though
    potential_new_source_ids = set()
    for event_id, source, posting_source_id in event_source_combos:
        batch_lookup.lookup_event(event_id)
        potential_new_source_ids.add(posting_source_id)
    batch_lookup.finish_loading()

    for event_id, source, posting_source_id in event_source_combos:
        fb_event = batch_lookup.data_for_event(event_id)
        if fb_event['deleted']:
            continue
        match_score = event_classifier.get_classified_event(fb_event).match_score()
        potential_events.make_potential_event_with_source(event_id, match_score, source=source, source_field=thing_db.FIELD_FEED)

    existing_source_ids = set([str(x.graph_id) for x in thing_db.Source.get_by_key_name(potential_new_source_ids) if x])
    new_source_ids = set([x for x in potential_new_source_ids if x not in existing_source_ids])
    for source_id in new_source_ids:
        #TODO(lambert): we know it doesn't exist, why does create_source_for_id check datastore?
        s = thing_db.Source(key_name=str(source_id))
        s.put()
    # initiate an out-of-band-scrape for our new sources we found
    if new_source_ids:
        deferred.defer(scrape_events_from_source_ids, batch_lookup.copy(), new_source_ids)

