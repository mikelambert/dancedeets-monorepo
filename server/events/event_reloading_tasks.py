import logging

from mapreduce import context
from mapreduce import operation as op

import app
import base_servlet
import fb_api
from users import users
from util import deferred
from util import fb_mapreduce
from util import mr
from . import eventdata
from . import event_updates

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

def add_event_tuple_if_updating(events_to_update, fbl, db_event, only_if_updated):
    try:
        fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id)
    except fb_api.NoFetchedDataException:
        # Ensure we can do a bare-minimum update, even if we aren't able to get a proper fb_event from the server.
        # This helps ensure we still update the event's search_time_period regardless.
        fb_event = db_event.fb_event
    update_regardless = not only_if_updated
    if fb_event['empty']:
        logging.info('The latest fb event %s is empty (%s), using dbevent.fb_event instead', db_event.id, fb_event['empty'])
        fb_event = db_event.fb_event
    if update_regardless or db_event.fb_event != fb_event:
        logging.info("Event %s is updated.", db_event.id)
        events_to_update.append((db_event, fb_event))
    # This happens when an event moves from TIME_FUTURE into TIME_PAST
    if event_updates.need_forced_update(db_event):
        logging.info("Event %s is being saved via forced update", db_event.fb_event_id)
        events_to_update.append((db_event, fb_event))


def load_fb_events_using_backup_tokens(event_ids, allow_cache, only_if_updated, disable_updates):
    db_events = eventdata.DBEvent.get_by_ids(event_ids)
    events_to_update = []
    for db_event in db_events:
        processed = False
        fbl = None
        logging.info("Looking for event id %s with visible user ids %s", db_event.fb_event_id, db_event.visible_to_fb_uids)
        for user in users.User.get_by_ids(db_event.visible_to_fb_uids):
            if not user:
                # If this user id doesn't exist in our system, then it was never an actual user
                # It most likely comes from the days when we could get fb events from friends-of-users
                continue
            fbl = user.get_fblookup()
            fbl.allow_cache = allow_cache
            try:
                fbl.request(fb_api.LookupEvent, db_event.fb_event_id)
                fbl.request(fb_api.LookupEventAttending, db_event.fb_event_id)
                fbl.request(fb_api.LookupEventAttendingMaybe, db_event.fb_event_id)
                fbl.batch_fetch()
                real_fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id)
            except fb_api.ExpiredOAuthToken:
                logging.warning("User %s has expired oauth token", user.fb_uid)
            else:
                if real_fb_event['empty'] != fb_api.EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS:
                    add_event_tuple_if_updating(events_to_update, fbl, db_event, only_if_updated)
                    processed = True
        # If we didn't process, it means none of our access_tokens are valid.
        if not processed:
            logging.warning('Cleaning out the visible_to_fb_uids for event %s, since our tokens have all expired.', db_event.fb_event_id)
            # Now mark our event as lacking in valid access_tokens, so that our pipeline can pick it up and look for a new one
            db_event.visible_to_fb_uids = []
            db_event.put()
            # Let's update the DBEvent as necessary (note, this uses the last-updated FBLookup)
            # Unfortunately, we failed to get anything in our fbl, as it was raising an ExpiredOAuthToken
            # So instead, let's call it and just have it use the db_event.fb_event
            if fbl:
                add_event_tuple_if_updating(events_to_update, fbl, db_event, only_if_updated)
    if events_to_update:
        event_updates.update_and_save_fb_events(events_to_update, disable_updates=disable_updates)

def yield_resave_display_event(fbl, all_events):
    event_updates.resave_display_events(all_events)
map_resave_display_event = fb_mapreduce.mr_wrap(yield_resave_display_event)

def yield_load_fb_event(fbl, all_events):
    ctx = context.get()
    if ctx:
        params = ctx.mapreduce_spec.mapper.params
        disable_updates = params['disable_updates']
        only_if_updated = params['only_if_updated']
    else:
        disable_updates = []
        only_if_updated = True

    # Process web_events
    web_events = [x for x in all_events if not x.is_fb_event]
    events_to_update = []
    for web_event in web_events:
        if event_updates.need_forced_update(web_event):
            events_to_update.append((web_event, web_event.web_event))
    event_updates.update_and_save_web_events(events_to_update, disable_updates=disable_updates)

    # Now process fb_events
    db_events = [x for x in all_events if x.is_fb_event]
    logging.info("loading db events %s", [db_event.fb_event_id for db_event in db_events])

    fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in db_events])
    fbl.request_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in db_events])
    # We load these too, just in case we want to check up on our auto-attendee criteria for events
    fbl.request_multi(fb_api.LookupEventAttendingMaybe, [x.fb_event_id for x in db_events])

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
        deferred.defer(load_fb_events_using_backup_tokens, empty_fb_event_ids, allow_cache=fbl.allow_cache, only_if_updated=only_if_updated, disable_updates=disable_updates)
    logging.info("Updating events: %s", [x[0].id for x in events_to_update])
    # And then re-save all the events in here
    if events_to_update:
        event_updates.update_and_save_fb_events(events_to_update, disable_updates=disable_updates)
map_load_fb_event = fb_mapreduce.mr_wrap(yield_load_fb_event)
load_fb_event = fb_mapreduce.nomr_wrap(yield_load_fb_event)


def mr_load_fb_events(fbl, display_event=False, load_attending=False, time_period=None, disable_updates=None, only_if_updated=True, queue='slow-queue'):
    if display_event:
        event_or_attending = 'Display Events'
        mr_func = 'map_resave_display_event'
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
        extra_mapper_params={'disable_updates': disable_updates, 'only_if_updated': only_if_updated},
        queue=queue,
    )

def yield_maybe_delete_bad_event(fbl, db_event):
    ctx = context.get()
    if ctx:
        params = ctx.mapreduce_spec.mapper.params
        allow_deletes = params['allow_deletes']
    else:
        allow_deletes = False

    if db_event.creating_method not in [eventdata.CM_AUTO_ATTENDEE, eventdata.CM_AUTO]:
        return

    if db_event.fb_event['empty']:
        return

    import datetime
    # This is when we started adding all sorts of "crap"
    if not db_event.creation_time or db_event.creation_time < datetime.datetime(2016, 3, 5):
        return

    logging.info('MDBE: Check on event %s: %s', db_event.id, db_event.creating_method)
    from event_scraper import auto_add
    from nlp import event_classifier
    classified_event = event_classifier.get_classified_event(db_event.fb_event)
    good_text_event = auto_add.is_good_event_by_text(db_event.fb_event, classified_event)
    if good_text_event:
        if db_event.creating_method != eventdata.CM_AUTO:
            db_event.creating_method = eventdata.CM_AUTO
            yield op.db.Put(db_event)
    else:
        good_event = auto_add.is_good_event_by_attendees(fbl, db_event.fb_event, classified_event=classified_event)
        if good_event:
            if db_event.creating_method != eventdata.CM_AUTO_ATTENDEE:
                db_event.creating_method = eventdata.CM_AUTO_ATTENDEE
                yield op.db.Put(db_event)
        else:
            logging.info('Accidentally %s added event %s: %s: %s', db_event.creating_method, db_event.fb_event_id, db_event.country, db_event.name)
            mr.increment('deleting-bad-event')
            result = '%s: %s: %s\n' % (db_event.fb_event_id, db_event.country, db_event.name)
            yield result.encode('utf-8')
            if allow_deletes:
                from search import search
                search.delete_from_fulltext_search_index(db_event.fb_event_id)
                yield op.db.Delete(db_event)
                display_event = search.DisplayEvent.get_by_id(db_event.fb_event_id)
                if display_event:
                    yield op.db.Delete(display_event)

map_maybe_delete_bad_event = fb_mapreduce.mr_wrap(yield_maybe_delete_bad_event)
maybe_delete_bad_event = fb_mapreduce.nomr_wrap(yield_maybe_delete_bad_event)

@app.route('/tasks/delete_bad_autoadds')
class DeleteBadAutoAddsHandler(base_servlet.EventOperationHandler):
    def get(self):
        time_period = self.request.get('time_period', None)
        queue = self.request.get('queue', 'fast-queue')
        filters = []
        if time_period:
            filters.append(('search_time_period', '=', time_period))
            name = 'Delete %s Bad Autoadds' % time_period
        else:
            name = 'Delete All Bad Autoadds'
        allow_deletes = self.request.get('allow_deletes', None) == '1'
        extra_mapper_params = {
            'allow_deletes': allow_deletes,
        }
        fb_mapreduce.start_map(
            fbl=self.fbl,
            name=name,
            handler_spec='events.event_reloading_tasks.map_maybe_delete_bad_event',
            entity_kind='events.eventdata.DBEvent',
            filters=filters,
            extra_mapper_params=extra_mapper_params,
            queue=queue,
            output_writer_spec='mapreduce.output_writers.GoogleCloudStorageOutputWriter',
            output_writer={
                'mime_type': 'text/plain',
                'bucket_name': 'dancedeets-hrd.appspot.com',
            },
        )
    post=get

@app.route('/tasks/load_events')
class LoadEventHandler(base_servlet.EventOperationHandler):
    event_operation = staticmethod(load_fb_event)

@app.route('/tasks/reload_events')
class ReloadEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        disable_updates = self.request.get('disable_updates', '').split(',')
        only_if_updated = self.request.get('only_if_updated', '1') != '0'
        time_period = self.request.get('time_period', None)
        load_attending = self.request.get('load_attending', '0') != '0'
        display_event = self.request.get('display_event', '0') != '0'
        queue = self.request.get('queue', 'slow-queue')
        mr_load_fb_events(self.fbl, display_event=display_event, load_attending=load_attending, time_period=time_period, disable_updates=disable_updates, only_if_updated=only_if_updated, queue=queue)
    post=get
