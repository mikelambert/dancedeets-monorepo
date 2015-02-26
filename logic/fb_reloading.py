import logging

from events import eventdata
from events import event_updates
import fb_api
from logic import pubsub
from util import fb_mapreduce
from util import timings

def mr_load_fb_event(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load Events',
        handler_spec='logic.fb_reloading.map_load_fb_event',
        handle_batch_size=20,
        entity_kind='events.eventdata.DBEvent'
    )

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


def mr_load_fb_event_attending(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load Event Attending',
        handler_spec='logic.fb_reloading.map_load_fb_event_attending',
        handle_batch_size=20,
        entity_kind='events.eventdata.DBEvent'
    )

@timings.timed
def yield_load_fb_event_attending(fbl, db_events):
    fbl.get_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in db_events])
map_load_fb_event_attending = fb_mapreduce.mr_wrap(yield_load_fb_event_attending)
load_fb_event_attending = fb_mapreduce.nomr_wrap(yield_load_fb_event_attending)


def mr_load_fb_user(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load Users',
        handler_spec='logic.fb_reloading.map_load_fb_user',
        entity_kind='users.users.User',
    )

@timings.timed
def yield_load_fb_user(fbl, user):
    if user.expired_oauth_token:
        logging.info("Skipping user %s (%s) due to expired access_token", user.fb_uid, user.full_name)
        return
    if not fbl.access_token:
        logging.info("Skipping user %s (%s) due to not having an access_token", user.fb_uid, user.full_name)
    try:
        fb_user = fbl.get(fb_api.LookupUser, user.fb_uid)
    except fb_api.ExpiredOAuthToken as e:
        logging.info("Auth token now expired, mark as such: %s", e)
        user.expired_oauth_token_reason = e.args[0]
        user.expired_oauth_token = True
        user.put()
        return
    else:
        user.compute_derived_properties(fb_user)
        user.put()
map_load_fb_user = fb_mapreduce.mr_user_wrap(yield_load_fb_user)
load_fb_user = fb_mapreduce.nomr_wrap(yield_load_fb_user)

def mr_load_past_fb_event(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load Past Events',
        handler_spec='logic.fb_reloading.map_load_fb_event',
        entity_kind='events.eventdata.DBEvent',
        filters=[('search_time_period', '=', eventdata.TIME_PAST)],
        handle_batch_size=20,
    )

def mr_load_future_fb_event(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load Future Events',
        handler_spec='logic.fb_reloading.map_load_fb_event',
        entity_kind='events.eventdata.DBEvent',
        filters=[('search_time_period', '=', eventdata.TIME_FUTURE)],
        handle_batch_size=20,
    )

def mr_load_all_fb_event(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load All Events',
        handler_spec='logic.fb_reloading.map_load_fb_event',
        handle_batch_size=20,
        entity_kind='events.eventdata.DBEvent',
    )


@timings.timed
def yield_post_jp_event(fbl, db_events):
    from mapreduce import context
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    token_nickname = params.get('token_nickname')
    db_events = [x for x in db_events if x.actual_city_name and x.actual_city_name.endswith('Japan')]
    for db_event in db_events:
        pubsub.eventually_publish_event(fbl, db_event.fb_event_id, token_nickname)
map_post_jp_event = fb_mapreduce.mr_wrap(yield_post_jp_event)

def mr_post_jp_events(fbl, token_nickname):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Post Future Japan Events',
        handler_spec='logic.fb_reloading.map_post_jp_event',
        entity_kind='events.eventdata.DBEvent',
        filters=[('search_time_period', '=', eventdata.TIME_FUTURE)],
        handle_batch_size=20,
        extra_mapper_params={'token_nickname': token_nickname},
    )

