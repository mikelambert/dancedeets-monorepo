import cgi
import logging
import urlparse

import facebook

from mapreduce import context
from mapreduce import control
#from mapreduce import operation as op

import fb_api
from logic import potential_events
from logic import thing_db

def scrape_events_from_sources(batch_lookup, sources):
    batch_lookup = batch_lookup.copy(allow_cache=False)
    for source in sources:
        batch_lookup.lookup_thing_feed(source.graph_id)
    batch_lookup.finish_loading()

    for source in sources:
        try:
            thing_feed = batch_lookup.data_for_thing_feed(source.graph_id)
            process_thing_feed(source, thing_feed)
        except fb_api.NoFetchedDataException, e:
            logging.error("Failed to fetch data for thing: %s", str(e))

def scrape_source(source):
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    fb_graph = facebook.GraphAPI(params['batch_lookup_fb_graph_access_token'])
    batch_lookup = fb_api.CommonBatchLookup(params['batch_lookup_fb_uid'], fb_graph, allow_cache=False) # Force refresh of thing feeds
    scrape_events_from_sources(batch_lookup, [source])

SOURCE_SCRAPER='SOURCE_SCRAPER'

def mapreduce_scrape_all_sources(batch_lookup):
    control.start_map(
        name='Scrape All Sources',
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec='logic.thing_scraper.scrape_source',
        mapper_parameters={
            'entity_kind': 'logic.thing_db.Source',
            'batch_lookup_fb_uid': batch_lookup.fb_uid,
            'batch_lookup_fb_graph_access_token': batch_lookup.fb_graph.access_token,
        },
        _app=SOURCE_SCRAPER,
    )

def process_thing_feed(source, thing_feed):
    # TODO(lambert): do we really need to scrape the 'info' to get the id, or we can we half the number of calls by just getting the feed?
    if 'data' not in thing_feed['feed']:
        logging.error("No 'data' found in: %s", thing_feed['feed'])
        return
    for post in thing_feed['feed']['data']:
        if 'link' in post:
            p = urlparse.urlparse(post['link'])
            if p.path.endswith('event.php'):
                qs = cgi.parse_qs(p.query)
                if 'eid' in qs:
                    eid = qs['eid'][0]
                    potential_events.save_potential_fb_event_ids([eid], source=source, source_field=thing_db.FIELD_FEED)
                else:
                    logging.error("broken link is %s", post['link'])



