import logging

import base_servlet
import fb_api
from util import fb_mapreduce
from util import timings
from . import search

def mr_refresh_index(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Refresh Search Index Events',
        handler_spec='search.search_tasks.map_refresh_event',
        handle_batch_size=20,
        entity_kind='events.eventdata.DBEvent'
    )

@timings.timed
def yield_refresh_event(fbl, db_events):
    logging.info("loading db events %s", [db_event.fb_event_id for db_event in db_events])
    fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in db_events])
    #fbl.request_multi(fb_api.LookupEventPageComments, [x.fb_event_id for x in db_events])
    fbl.batch_fetch()
    for db_event in db_events:
        try:
            fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id)
            search.update_fulltext_search_index(db_event, fb_event)
        except fb_api.NoFetchedDataException, e:
            logging.info("No data fetched for event id %s: %s", db_event.fb_event_id, e)
map_refresh_event = fb_mapreduce.mr_wrap(yield_refresh_event)
refresh_event = fb_mapreduce.nomr_wrap(yield_refresh_event)


class MemcacheFutureEvents(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        search.memcache_future_events(self.fbl)

class RefreshFulltextSearchIndex(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        index_future = bool(int(self.request.get('index_future', 1)))
        if index_future:
            search.construct_fulltext_search_index(self.fbl, index_future=index_future)
        else:
            mr_refresh_index(self.fbl)
