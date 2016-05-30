import logging

import fb_api
from events import eventdata
from logic import backgrounder
from util import dates


def get_decorated_user_events(fbl):
    events = _get_user_events(fbl)
    events = _decorate_with_loaded(events)
    return events


def _get_user_events(fbl):
    try:
        user_events = fbl.get(fb_api.LookupUserEvents, fbl.fb_uid, allow_cache=False)
    except fb_api.NoFetchedDataException as e:
        try:
            user_events = fbl.get(fb_api.LookupUserEvents, fbl.fb_uid)
        except fb_api.NoFetchedDataException, e:
            logging.error("Could not load event info for user: %s", e)
            user_events = None
    if user_events is not None:
        results_json = fb_api.LookupUserEvents.all_events(user_events)
        events = list(sorted(results_json, key=lambda x: x.get('start_time')))
    else:
        events = []
    return events


def _decorate_with_loaded(events):
    loaded_fb_events = eventdata.DBEvent.get_by_ids([x['id'] for x in events])
    loaded_fb_event_lookup = dict((x.key.string_id(), x) for x in loaded_fb_events if x)

    for event in events:
        event['loaded'] = event['id'] in loaded_fb_events

    _hack_reload(loaded_fb_event_lookup, events)

    keys = ['loaded'] + fb_api.LookupUserEvents.fields
    canonicalized_events = [dict((k, e[k]) for k in keys if k in e) for e in events]
    return canonicalized_events


def _hack_reload(loaded_fb_event_lookup, events):
    # HACK: if we detected different data between the FB pseudo-event data and our local events, trigger a refresh
    # This can happen if a user takes an 'old' event that has become PAST, and puts the event in the future,
    # bypassing our optimization attempts to only refresh FUTURE/ONGOING events. This is a fail-safe for that.
    reload_event_ids = []
    for event in events:
        loaded_event = loaded_fb_event_lookup.get(event['id'])
        if loaded_event and loaded_event.start_time != dates.parse_fb_timestamp(event['start_time']):
            reload_event_ids.append(event['id'])

    if reload_event_ids:
        logging.info("Dates changed, reloading events: %s", reload_event_ids)
        backgrounder.load_events(reload_event_ids, allow_cache=False)
