import datetime
import logging

from events import eventdata
import fb_api
from logic import email_events
from logic import potential_events
from logic import search
from util import dates
from util import fb_mapreduce
from util import timings

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
            fb_event = batch_lookup.data_for_event(db_event.fb_event_id, only_if_updated=True)

            #TODO(lambert): refactor this logic to a central place!
            one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
            event_end_time = dates.faked_end_time(db_event.start_time, db_event.end_time)
            how_far_in_past = (one_day_ago - event_end_time).total_seconds()
            recently_became_past = (how_far_in_past > 0 and how_far_in_past < 3*24*60*60)
            # Force an update for events that recently went into the past, to get TIME_PAST set
            #TODO(lambert): this is a major hack!!! :-(
            # Events that change due to facebook, should be updated in db and index
            # We need to capture attendee-changes (in the fb_event_attending updates)!
            # Events that change due to time-passing, are currently not-handled-well-at-all...this forces it, via an ugly hack.
            if recently_became_past:
                fb_event = batch_lookup.data_for_event(db_event.fb_event_id)
            if fb_event:
                # NOTE: This update is most likely due to a change in the all-members of the event.
                # We should decide if this is worth tracking/keeping somehow, as it may be worth skipping?
                logging.info("FBevent %s updated, saving and indexing DBevent", fb_event['info']['id'])
                db_event.make_findable_for(batch_lookup, fb_event)
                db_event.put()
                search.update_fulltext_search_index(db_event, fb_event)
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


