import logging

from mapreduce import context

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
    events_to_update = []
    for db_event in db_events:
        try:
            fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id, only_if_updated=True)
            if event_updates.need_forced_update(db_event):
                fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id)
            if fb_event:
                events_to_update.append((db_event, fb_event))
        except fb_api.NoFetchedDataException, e:
            logging.info("No data fetched for event id %s: %s", db_event.fb_event_id, e)
    ctx = context.get()
    if ctx:
        params = ctx.mapreduce_spec.mapper.params
        update_geodata = params['update_geodata']
    else:
        update_geodata = True
    event_updates.update_and_save_events(events_to_update, update_geodata=update_geodata)
map_load_fb_event = fb_mapreduce.mr_wrap(yield_load_fb_event)
load_fb_event = fb_mapreduce.nomr_wrap(yield_load_fb_event)


@timings.timed
def yield_load_fb_event_attending(fbl, db_events):
    fbl.get_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in db_events])
map_load_fb_event_attending = fb_mapreduce.mr_wrap(yield_load_fb_event_attending)
load_fb_event_attending = fb_mapreduce.nomr_wrap(yield_load_fb_event_attending)

def mr_load_fb_events(fbl, time_period=None, update_geodata=True, queue='slow-queue'):
    if time_period:
        filters = [('search_time_period', '=', time_period)]
        name = 'Load %s Events' % time_period
    else:
        filters = []
        name = 'Load All Events'
    fb_mapreduce.start_map(
        fbl=fbl,
        name=name,
        handler_spec='events.event_reloading_tasks.map_load_fb_event',
        entity_kind='events.eventdata.DBEvent',
        handle_batch_size=20,
        filters=filters,
        extra_mapper_params={'update_geodata': update_geodata},
        queue=queue,
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
        update_geodata = self.request.get('update_geodata') != '0'
        mr_load_fb_events(self.fbl, time_period=dates.TIME_PAST, update_geodata=update_geodata)
    post=get

class ReloadFutureEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        update_geodata = self.request.get('update_geodata') != '0'
        mr_load_fb_events(self.fbl, time_period=dates.TIME_FUTURE, update_geodata=update_geodata)
    post=get

class ReloadAllEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        update_geodata = self.request.get('update_geodata') != '0'
        queue = self.request.get('queue', 'slow-queue')
        mr_load_fb_events(self.fbl, update_geodata=update_geodata, queue=queue)
    post=get
