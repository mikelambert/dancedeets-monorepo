import logging

import base_servlet
import fb_api
from util import dates
from util import fb_mapreduce
from util import timings
from . import eventdata
from . import event_updates

@timings.timed
def yield_load_fb_event(fbl, db_events):
    logging.info("loading db events %s", [db_event.fb_event_id for db_event in db_events])
    fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in db_events])
    #fbl.request_multi(fb_api.LookupEventPageComments, [x.fb_event_id for x in db_events])
    fbl.batch_fetch()
    for db_event in db_events:
        try:
            fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id, only_if_updated=True)
            if event_updates.need_forced_update(db_event):
                fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id)
            if fb_event:
                logging.info("FBEvent %s changed, will try to save and index DBEvent", db_event.fb_event_id)
                event_updates.update_and_save_event(db_event, fb_event)
        except fb_api.NoFetchedDataException, e:
            logging.info("No data fetched for event id %s: %s", db_event.fb_event_id, e)
map_load_fb_event = fb_mapreduce.mr_wrap(yield_load_fb_event)
load_fb_event = fb_mapreduce.nomr_wrap(yield_load_fb_event)


@timings.timed
def yield_load_fb_event_attending(fbl, db_events):
    fbl.get_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in db_events])
map_load_fb_event_attending = fb_mapreduce.mr_wrap(yield_load_fb_event_attending)
load_fb_event_attending = fb_mapreduce.nomr_wrap(yield_load_fb_event_attending)

def mr_load_past_fb_event(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load Past Events',
        handler_spec='events.event_reloading_tasks.map_load_fb_event',
        entity_kind='events.eventdata.DBEvent',
        filters=[('search_time_period', '=', dates.TIME_PAST)],
        handle_batch_size=20,
    )

def mr_load_future_fb_event(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load Future Events',
        handler_spec='events.event_reloading_tasks.map_load_fb_event',
        entity_kind='events.eventdata.DBEvent',
        filters=[('search_time_period', '=', dates.TIME_FUTURE)],
        handle_batch_size=20,
    )

def mr_load_all_fb_event(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load All Events',
        handler_spec='events.event_reloading_tasks.map_load_fb_event',
        handle_batch_size=20,
        entity_kind='events.eventdata.DBEvent',
    )

class LoadEventHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        db_events = [x for x in eventdata.DBEvent.get_by_ids(event_ids) if x]
        load_fb_event(self.fbl, db_events)
    post=get

class LoadEventAttendingHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        db_events = [x for x in eventdata.DBEvent.get_by_ids(event_ids) if x]
        load_fb_event_attending(self.fbl, db_events)
    post=get

class ReloadPastEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        mr_load_past_fb_event(self.fbl)
    post=get

class ReloadFutureEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        mr_load_future_fb_event(self.fbl)
    post=get

class ReloadAllEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        mr_load_all_fb_event(self.fbl)
    post=get
