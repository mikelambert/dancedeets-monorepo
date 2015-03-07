import logging

import fb_api
from . import auto_add
from . import potential_events
from . import thing_db

def get_potential_dance_events(fbl, user_id, fb_user_events):
    # The source_id is not fbl.fb_uid, because sometimes we fetch friend's events as Mike, and the source is not Mike.
    results_json = fb_user_events['all_event_info']['data']
    #STR_ID_MIGRATE: We still get ids as ints from our FQL
    event_ids = [str(x['eid']) for x in sorted(results_json, key=lambda x: x.get('start_time'))]

    logging.info("For user id %s, found %s invited events %s", user_id, len(event_ids), event_ids)

    # TODO(lambert): instead of this, perhaps we want to store the "previous list of ids from this users invites", or compare versus the previous all_event_info object?
    existing_potential_events = potential_events.PotentialEvent.get_by_key_name(event_ids)
    tracked_potential_event_ids = [x.fb_event_id for x in existing_potential_events if x and x.has_source_with_field(user_id, thing_db.FIELD_INVITES)]
    logging.info("For user id %s, already %s tracking potential events for %s", user_id, len(tracked_potential_event_ids), tracked_potential_event_ids)

    event_ids = set(event_ids).difference(tracked_potential_event_ids) # only handle new ids
    logging.info("For user id %s, leaves %s events to process", user_id, len(event_ids))

    # Only do 150 events a time so we don't blow up memory
    # TODO(lambert): Maybe do something whereby we don't load fb-events for things we just need to add a source-id on, and only load for things without a potential-event at all. Will need to change the make_potential_event_with_source() API around though...perhaps it's about time.
    if len(event_ids) > 150:
        logging.info("Trimming to 150 events so we don't blow through memory, we'll get the rest of the events next time we run...")
        event_ids = sorted(event_ids)[:150]

    source = thing_db.create_source_for_id(user_id, fb_data=None)
    source.put()

    logging.info("Going to look up %s events", len(event_ids))

    fbl.request_multi(fb_api.LookupEvent, event_ids)
    #DISABLE_ATTENDING
    #fbl.request_multi(fb_api.LookupEventAttending, event_ids)
    fbl.batch_fetch()

    pe_events = []
    fb_events = []
    for event_id in event_ids:
        try:
            fb_event = fbl.fetched_data(fb_api.LookupEvent, event_id)
            #DISABLE_ATTENDING
            fb_event_attending = None
            #fb_event_attending = fbl.fetched_data(fb_api.LookupEventAttending, event_id)
        except fb_api.NoFetchedDataException:
            logging.info("event id %s: no fetched data", event_id)
            continue # must be a non-saved event, probably due to private/closed event. so ignore.
        if fb_event['empty'] or not fb_api.is_public_ish(fb_event):
            logging.info("event id %s: deleted, or private", event_id)
            continue # only legit events
        pe_event = potential_events.make_potential_event_with_source(event_id, fb_event, fb_event_attending, source=source, source_field=thing_db.FIELD_INVITES)
        pe_events.append(pe_event)
        fb_events.append(fb_event)
    logging.info("Going to classify the %s potential events", len(event_ids))
    # Classify events on the fly as we add them as potential events, instead of waiting for the mapreduce
    auto_add.classify_events(fbl, pe_events, fb_events)
    
