import logging

import fb_api
from notifications import rsvped_events
from util import fb_mapreduce
from . import scrape_user_potential_events


def mr_load_potential_events(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Load Potential Events For Users',
        handler_spec='event_scraper.potential_events_reloading.map_load_potential_events',
        entity_kind='users.users.User',
    )


def load_potential_events_for_user(user):
    fbl = fb_api.FBLookup(user.fb_uid, user.fb_access_token)
    fbl.allow_cache = False
    load_potential_events_for_user_ids(fbl, [user.fb_uid])


def load_potential_events_for_user_ids(fbl, user_ids):
    user_events_list = fbl.get_multi(fb_api.LookupUserEvents, user_ids)
    # Since we've loaded the latest events from the user, allow future event lookups to come from cache
    fbl.allow_cache = True
    for user_id, user_events in zip(user_ids, user_events_list):
        scrape_user_potential_events.get_potential_dance_events(fbl, user_id, user_events)


def map_load_potential_events(user):
    fbl = fb_mapreduce.get_fblookup(user)
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
        rsvped_events.setup_reminders(user.fb_uid, user_events)
