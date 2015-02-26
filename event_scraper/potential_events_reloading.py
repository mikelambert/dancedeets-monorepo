import logging

import fb_api
from util import fb_mapreduce
from util import timings
from . import scrape_user_potential_events

def mr_load_potential_events(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load Potential Events For Users',
        handler_spec='event_scraper.potential_events_reloading.map_load_potential_events',
        entity_kind='users.users.User',
    )

@timings.timed
def load_potential_events_for_user_ids(fbl, user_ids):
    user_events_list = fbl.get_multi(fb_api.LookupUserEvents, user_ids)
    # Since we've loaded the latest events from the user, allow future event lookups to come from cache
    fbl.allow_cache = True
    for user_id, user_events in zip(user_ids, user_events_list):
        scrape_user_potential_events.get_potential_dance_events(fbl, user_id, user_events)

def yield_load_potential_events(fbl, user):
    if user.expired_oauth_token:
        return
    try:
        user_events = fbl.get(fb_api.LookupUserEvents, user.fb_uid)
    except fb_api.ExpiredOAuthToken as e:
        logging.warning("Auth token now expired, skip for now until user-load fixes this: %s", e)
        # or do we want to fix-and-put here
        #user.expired_oauth_token_reason = e.args[0]
        #user.expired_oauth_token = True
        #user.put()
        #return
    else:
        # Since we've loaded the latest events from the user, allow future event lookups to come from cache
        fbl.allow_cache = True
        scrape_user_potential_events.get_potential_dance_events(fbl, user.fb_uid, user_events)

map_load_potential_events = fb_mapreduce.mr_user_wrap(yield_load_potential_events)
load_potential_events = fb_mapreduce.nomr_wrap(yield_load_potential_events)
