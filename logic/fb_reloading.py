import logging

from google.appengine.datastore import datastore_query

from events import eventdata
import fb_api
from logic import email_events
from logic import potential_events
from util import fb_mapreduce
from util import timings
from util import mr_helper

BROKEN_UIDS = []#"1400235949", "1268158596"]

def mr_load_fb_event(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load Events',
                handler_spec='logic.fb_reloading.map_load_fb_event',
                handle_batch_size=20,
                entity_kind='events.eventdata.DBEvent'
        )

@timings.timed
def yield_load_fb_event(batch_lookup, db_events):
    logging.info("loading db events %s", [db_event.fb_event_id for db_event in db_events])
    for db_event in db_events:
        batch_lookup.lookup_event(db_event.fb_event_id)
    batch_lookup.finish_loading()
    for db_event in db_events:
        try:
            fb_event = batch_lookup.data_for_event(db_event.fb_event_id)
            db_event.make_findable_for(batch_lookup, fb_event)
            db_event.put()
        except fb_api.NoFetchedDataException:
            logging.info("No data fetched for event id %s", db_event.fb_event_id)
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
def yield_load_fb_event_attending(batch_lookup, db_events):
    for db_event in db_events:
        batch_lookup.lookup_event_attending(db_event.fb_event_id)
    batch_lookup.finish_loading()
    for db_event in db_events:
        fb_event_attending = batch_lookup.data_for_event_attending(db_event.fb_event_id)
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
def yield_load_fb_user(batch_lookup, user):
    if user.expired_oauth_token:
        return
    # TODO(lambert): figure out why future's data can't be loaded
    if str(user.fb_uid) in BROKEN_UIDS:
        return
        batch_lookup.lookup_user(user.fb_uid)
    try:
        batch_lookup.finish_loading()
            fb_user = batch_lookup.data_for_user(user.fb_uid)
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

class FutureEventInputReader(mr_helper.FilteredInputReader):
    def filter_query(self, query):
        query.filter('search_time_period =', eventdata.TIME_FUTURE)

class PastEventInputReader(mr_helper.FilteredInputReader):
    def filter_query(self, query):
        query.filter('search_time_period =', eventdata.TIME_PAST)

def mr_load_past_fb_event(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load Past Events',
                handler_spec='logic.fb_reloading.map_load_fb_event',
                entity_kind='events.eventdata.DBEvent',
        handle_batch_size=20,
        reader_spec='logic.fb_reloading.PastEventInputReader',
        )

def mr_load_future_fb_event(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load Future Events',
                handler_spec='logic.fb_reloading.map_load_fb_event',
                entity_kind='events.eventdata.DBEvent',
        handle_batch_size=20,
        reader_spec='logic.fb_reloading.FutureEventInputReader',
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
def yield_email_user(batch_lookup, user):
        batch_lookup.lookup_user(user.fb_uid)
        batch_lookup.lookup_user_events(user.fb_uid)
    try:
        batch_lookup.finish_loading()
    except fb_api.ExpiredOAuthToken, e:
        logging.info("Auth token now expired, mark as such: %s", e)
        user.expired_oauth_token_reason = e.args[0]
        user.expired_oauth_token = True
        user.put()
        return None
    return email_events.email_for_user(user, batch_lookup, batch_lookup.fb_graph, should_send=True)
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
def load_potential_events_for_user_ids(batch_lookup, user_ids):
    # TODO(lambert): figure out why future's data can't be loaded
    user_ids = set(user_ids).difference(BROKEN_UIDS)
    for user_id in user_ids:
        batch_lookup.lookup_user_events(user_id)
    batch_lookup.finish_loading()
    for user_id in user_ids:
        potential_events.get_potential_dance_events(batch_lookup, user_id)

def yield_load_potential_events(batch_lookup, user):
    if user.expired_oauth_token:
        return
    load_potential_events_for_user_ids(batch_lookup, [user.fb_uid])
map_load_potential_events = fb_mapreduce.mr_user_wrap(yield_load_potential_events)
load_potential_events = fb_mapreduce.nomr_wrap(yield_load_potential_events)


