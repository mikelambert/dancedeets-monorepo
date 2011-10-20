import cgi
import logging
import urlparse

import facebook

import fb_api
from logic import potential_events
from logic import thing_db

from util import fb_mapreduce

def scrape_events_from_sources(batch_lookup, sources):
    batch_lookup = batch_lookup.copy(allow_cache=False)
    for source in sources:
        batch_lookup.lookup_thing_feed(source.graph_id)
    batch_lookup.finish_loading()

    event_ids = []
    for source in sources:
        try:
            thing_feed = batch_lookup.data_for_thing_feed(source.graph_id)
            event_ids.extend(process_thing_feed(source, thing_feed))
        except fb_api.NoFetchedDataException, e:
            logging.error("Failed to fetch data for thing: %s", str(e))
    return event_ids

def scrape_source(source):
    batch_lookup = fb_mapreduce.get_batch_lookup(allow_cache=False) # Force refresh of thing feeds
    event_ids = scrape_events_from_sources(batch_lookup, [source])

def mapreduce_scrape_all_sources(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup,
        'Scrape All Sources',
        'logic.thing_scraper.scrape_source',
        'logic.thing_db.Source'
    )

def create_source_from_event(event):
    batch_lookup = fb_mapreduce.get_batch_lookup()
    thing_db.create_source_from_event(event, batch_lookup)

def mapreduce_create_sources_from_events(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup,
        'Create Sources from Events',
        'logic.thing_scraper.create_source_from_event',
        'events.eventdata.DBEvent'
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
    source.put()

    event_ids = []
    new_source_ids = []
    for post in thing_feed['feed']['data']:
        if 'link' in post:
            p = urlparse.urlparse(post['link'])
            if p.netloc == 'www.facebook.com' and p.path == '/event.php':
                qs = cgi.parse_qs(p.query)
                if 'eid' in qs:
                    eid = qs['eid'][0]
                    potential_events.save_potential_fb_event_ids([eid], source=source, source_field=thing_db.FIELD_FEED)
                    event_ids.append(eid)
                    if 'from' in post:
                        new_source_ids.append(post['from']['id'])
                else:
                    logging.error("broken link is %s", post['link'])

    for s_id in new_source_ids:
        s = thing_db.create_source_for_id(s_id)
        s.put()
        

    return event_ids
