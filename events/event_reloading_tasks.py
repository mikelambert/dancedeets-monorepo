import datetime
import logging

from google.appengine.ext import deferred
from mapreduce import context

import app
import base_servlet
import fb_api
from util import fb_mapreduce
from users import users
from . import eventdata
from . import event_updates

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

def add_event_tuple_if_updating(events_to_update, fbl, db_event, only_if_updated):
    fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id, only_if_updated=only_if_updated)
    # This happens when an event moves from TIME_FUTURE into TIME_PAST
    logging.info("Event %s is%s updated.", db_event.id, " not" if not fb_event else "")
    if event_updates.need_forced_update(db_event):
        fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.id)
        logging.info("Event %s is being saved via forced update", db_event.fb_event_id)
    # If we have an event in need of updating, record that
    if fb_event:
        events_to_update.append((db_event, fb_event))


def load_fb_events_using_backup_tokens(event_ids, allow_cache, only_if_updated, update_geodata):
    db_events = eventdata.DBEvent.get_by_ids(event_ids)
    events_to_update = []
    for db_event in db_events:
        processed = False
        fbl = None
        logging.info("Looking for event id %s with visible user ids %s", db_event.fb_event_id, db_event.visible_to_fb_uids)
        for user in users.User.get_by_ids(db_event.visible_to_fb_uids):
            fbl = user.get_fblookup()
            fbl.allow_cache = allow_cache
            try:
                real_fb_event = fbl.get(fb_api.LookupEvent, db_event.fb_event_id)
            except fb_api.ExpiredOAuthToken:
                logging.warning("User %s has expired oauth token", user.fb_uid)
            else:
                if real_fb_event['empty'] != fb_api.EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS:
                    add_event_tuple_if_updating(events_to_update, fbl, db_event, only_if_updated)
                    processed = True
        # If we didn't process, it means none of our access_tokens are valid.
        if not processed:
            # Now mark our event as lacking in valid access_tokens, so that our pipeline can pick it up and look for a new one
            db_event.visible_to_fb_uids = []
            db_event.put()
            # Let's update the DBEvent as necessary (note, this uses the last-updated FBLookup)
            if fbl:
                add_event_tuple_if_updating(events_to_update, fbl, db_event, only_if_updated)
    event_updates.update_and_save_fb_events(events_to_update, update_geodata=update_geodata)


def yield_load_fb_event(fbl, all_events):
    ctx = context.get()
    if ctx:
        params = ctx.mapreduce_spec.mapper.params
        update_geodata = params['update_geodata']
        only_if_updated = params['only_if_updated']
    else:
        update_geodata = True
        only_if_updated = True

    # Process web_events
    web_events = [x for x in all_events if not x.is_fb_event]
    events_to_update = []
    for web_event in web_events:
        if event_updates.need_forced_update(web_event):
            events_to_update.append((web_event, web_event.web_event))
    event_updates.update_and_save_web_events(events_to_update, update_geodata=update_geodata)

    # Now process fb_events
    db_events = [x for x in all_events if x.is_fb_event]
    logging.info("loading db events %s", [db_event.fb_event_id for db_event in db_events])
    fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in db_events])
    # fbl.request_multi(fb_api.LookupEventPageComments, [x.fb_event_id for x in db_events])
    fbl.batch_fetch()
    events_to_update = []
    empty_fb_event_ids = []
    for db_event in db_events:
        try:
            real_fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id)
            # If it's an empty fb_event with our main access token, and we have other tokens we'd like to try...
            # If there are no visible_to_fb_uids and we don't have permissions, then we don't do this...
            #
            # TODO: This would happen on event deletion?
            #
            # TODO: Also, who sets visible_to_fb_uids? Why didn't this event have any?
            # TODO: Who re-sets visible_to_fb_uids after it goes empty? Can we ensure that keeps going?
            #
            # TODO: And what happens if we have a deleted event, with visible_to_fb_uids, that we attempt to run and query, and nothing happens?
            # Should we distinguish between deleted (and inaccessible) and permissions-lost-to-token (and inaccessible)?
            #
            # TODO: Why doesn't this update the event? Because add_event_tuple_if_updating seems to do nothing, probably because no fb_event is returned
            if real_fb_event['empty'] == fb_api.EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS and db_event.visible_to_fb_uids:
                empty_fb_event_ids.append(db_event.fb_event_id)
            else:
                # Otherwise if it's visible to our main token, or there are no other tokens to try, deal with it here.
                add_event_tuple_if_updating(events_to_update, fbl, db_event, only_if_updated)
        except fb_api.NoFetchedDataException as e:
            logging.info("No data fetched for event id %s: %s", db_event.fb_event_id, e)
    # Now trigger off a background reloading of empty fb_events
    if empty_fb_event_ids:
        logging.info("Couldn't fetch, using backup tokens for events: %s", empty_fb_event_ids)
        deferred.defer(load_fb_events_using_backup_tokens, empty_fb_event_ids, allow_cache=fbl.allow_cache, only_if_updated=only_if_updated, update_geodata=update_geodata)
    logging.info("Updating events: %s", [x[0].id for x in events_to_update])
    # And then re-save all the events in here
    event_updates.update_and_save_fb_events(events_to_update, update_geodata=update_geodata)
map_load_fb_event = fb_mapreduce.mr_wrap(yield_load_fb_event)
load_fb_event = fb_mapreduce.nomr_wrap(yield_load_fb_event)


def yield_load_fb_event_attending(fbl, all_events):
    db_events = [x for x in all_events if x.is_fb_event]
    fbl.get_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in db_events], allow_fail=True)
map_load_fb_event_attending = fb_mapreduce.mr_wrap(yield_load_fb_event_attending)
load_fb_event_attending = fb_mapreduce.nomr_wrap(yield_load_fb_event_attending)


def mr_load_fb_events(fbl, load_attending=False, time_period=None, update_geodata=True, only_if_updated=True, queue='slow-queue'):
    if load_attending:
        event_or_attending = 'Event Attendings'
        mr_func = 'map_load_fb_event_attending'
    else:
        event_or_attending = 'Events'
        mr_func = 'map_load_fb_event'
    filters = []
    if time_period:
        filters.append(('search_time_period', '=', time_period))
        name = 'Load %s %s' % (time_period, event_or_attending)
    else:
        name = 'Load All %s' % (event_or_attending)
    fb_mapreduce.start_map(
        fbl=fbl,
        name=name,
        handler_spec='events.event_reloading_tasks.%s' % mr_func,
        entity_kind='events.eventdata.DBEvent',
        handle_batch_size=20,
        filters=filters,
        extra_mapper_params={'update_geodata': update_geodata, 'only_if_updated': only_if_updated},
        queue=queue,
    )



@app.route('/tasks/load_events')
class LoadEventHandler(base_servlet.EventOperationHandler):
    event_operation = load_fb_event


@app.route('/tasks/load_event_attending')
class LoadEventAttendingHandler(base_servlet.EventOperationHandler):
    event_operation = load_fb_event_attending


@app.route('/tasks/reload_events')
class ReloadEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        update_geodata = self.request.get('update_geodata', '1') != '0'
        only_if_updated = self.request.get('only_if_updated', '1') != '0'
        time_period = self.request.get('time_period', None)
        load_attending = self.request.get('load_attending', '0') != '0'
        queue = self.request.get('queue', 'slow-queue')
        mr_load_fb_events(self.fbl, load_attending=load_attending, time_period=time_period, update_geodata=update_geodata, only_if_updated=only_if_updated, queue=queue)
    post=get
