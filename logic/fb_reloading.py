import logging

from events import eventdata
import fb_api
from logic import email_events
from logic import event_updates
from logic import potential_events
from util import fb_mapreduce
from util import timings

def mr_load_fb_event(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='Load Events',
        handler_spec='logic.fb_reloading.map_load_fb_event',
        handle_batch_size=20,
        entity_kind='events.eventdata.DBEvent'
    )

@timings.timed
def yield_load_fb_event(fbl, db_events):
    fbl = fb_api.massage_fbl(fbl)
    logging.info("loading db events %s", [db_event.fb_event_id for db_event in db_events])
    fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in db_events])
    fbl.batch_fetch()
    for db_event in db_events:
        try:
            fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id, only_if_updated=True)
            if event_updates.need_forced_update(db_event):
                fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id)
            if fb_event:
                logging.info("FBEvent %s changed, will try to save and indexing DBEvent", db_event.fb_event_id)
                event_updates.update_and_save_event(db_event, fb_event)
        except fb_api.NoFetchedDataException, e:
            logging.info("No data fetched for event id %s: %s", db_event.fb_event_id, e)
map_load_fb_event = fb_mapreduce.mr_wrap(yield_load_fb_event)
load_fb_event = fb_mapreduce.nomr_wrap(yield_load_fb_event)


def mr_load_fb_event_attending(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='Load Event Attending',
        handler_spec='logic.fb_reloading.map_load_fb_event_attending',
        handle_batch_size=20,
        entity_kind='events.eventdata.DBEvent'
    )

@timings.timed
def yield_load_fb_event_attending(fbl, db_events):
    fbl = fb_api.massage_fbl(fbl)
    fbl.request_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in db_events])
    fbl.batch_fetch()
    for db_event in db_events:
        fb_event_attending = fbl.fetched_data(fb_api.LookupEventAttending, db_event.fb_event_id)
        db_event.include_attending_summary(fb_event_attending)
        db_event.put()
map_load_fb_event_attending = fb_mapreduce.mr_wrap(yield_load_fb_event_attending)
load_fb_event_attending = fb_mapreduce.nomr_wrap(yield_load_fb_event_attending)


def mr_load_fb_user(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='Load Users',
        handler_spec='logic.fb_reloading.map_load_fb_user',
        entity_kind='events.users.User',
    )

@timings.timed
def yield_load_fb_user(fbl, user):
    fbl = fb_api.massage_fbl(fbl)
    if user.expired_oauth_token:
        return
    fbl.request(fb_api.LookupUser, user.fb_uid)
    try:
        fbl.batch_fetch()
        fb_user = fbl.fetched_data(fb_api.LookupUser, user.fb_uid)
    except (fb_api.ExpiredOAuthToken, fb_api.NoFetchedDataException), e:
        logging.info("Auth token now expired, mark as such: %s", e)
        user.expired_oauth_token_reason = e.args[0]
        user.expired_oauth_token = True
        user.put()
        return
    user.compute_derived_properties(fb_user)
    user.put()
map_load_fb_user = fb_mapreduce.mr_user_wrap(yield_load_fb_user)
load_fb_user = fb_mapreduce.nomr_wrap(yield_load_fb_user)

def mr_load_past_fb_event(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='Load Past Events',
        handler_spec='logic.fb_reloading.map_load_fb_event',
        entity_kind='events.eventdata.DBEvent',
        filters=[('search_time_period', '=', eventdata.TIME_PAST)],
        handle_batch_size=20,
    )

def mr_load_future_fb_event(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='Load Future Events',
        handler_spec='logic.fb_reloading.map_load_fb_event',
        entity_kind='events.eventdata.DBEvent',
        filters=[('search_time_period', '=', eventdata.TIME_FUTURE)],
        handle_batch_size=20,
    )

def mr_load_all_fb_event(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='Load All Events',
        handler_spec='logic.fb_reloading.map_load_fb_event',
        handle_batch_size=20,
        entity_kind='events.eventdata.DBEvent',
    )


def mr_email_user(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='Email Users',
        #TODO: MOVE
        handler_spec='logic.fb_reloading.map_email_user',
        entity_kind='events.users.User',
    )

#TODO(lambert): do we really want yield on this one?
@timings.timed
def yield_email_user(fbl, user):
    fbl = fb_api.massage_fbl(fbl)
    fbl.request(fb_api.LookupUser, user.fb_uid)
    fbl.request(fb_api.LookupUserEvents, user.fb_uid)
    try:
        fbl.batch_fetch()
    except fb_api.ExpiredOAuthToken, e:
        logging.info("Auth token now expired, mark as such: %s", e)
        user.expired_oauth_token_reason = e.args[0]
        user.expired_oauth_token = True
        user.put()
        return None
    return email_events.email_for_user(user, fbl, should_send=True)
map_email_user = fb_mapreduce.mr_user_wrap(yield_email_user)
email_user = fb_mapreduce.nomr_wrap(yield_email_user)

def mr_load_potential_events(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='Load Potential Events For Users',
        handler_spec='logic.fb_reloading.map_load_potential_events',
        entity_kind='events.users.User',
    )

@timings.timed
def load_potential_events_for_user_ids(fbl, user_ids):
    fbl = fb_api.massage_fbl(fbl)
    fbl.get_multi(fb_api.LookupUserEvents, user_ids)
    fbl.batch_fetch()
    for user_id in user_ids:
        user_events = fbl.fetched_data(fb_api.LookupUserEvents, user_id)
        potential_events.get_potential_dance_events(fbl, user_events)

def yield_load_potential_events(batch_lookup, user):
    if user.expired_oauth_token:
        return
    load_potential_events_for_user_ids(batch_lookup, [user.fb_uid])
map_load_potential_events = fb_mapreduce.mr_user_wrap(yield_load_potential_events)
load_potential_events = fb_mapreduce.nomr_wrap(yield_load_potential_events)


