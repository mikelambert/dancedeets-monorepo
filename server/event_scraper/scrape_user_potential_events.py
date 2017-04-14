import logging

import fb_api
from . import event_pipeline
from . import potential_events
from . import thing_db


def get_potential_dance_events(fbl, user_id, fb_user_events):
    results_json = fb_api.LookupUserEvents.all_events(fb_user_events)

    event_ids = [x['id'] for x in sorted(results_json, key=lambda x: x.get('start_time'))]

    logging.info("For user id %s, found %s invited events %s", user_id, len(event_ids), event_ids)

    source = thing_db.create_source_for_id(user_id, fb_data=None)
    source.put()

    discovered_list = [potential_events.DiscoveredEvent(x, source, thing_db.FIELD_INVITES) for x in event_ids]
    discovered_list_to_process = event_pipeline.get_unprocessed_discovered_events(discovered_list)
    logging.info("For user id %s, removing discovered, leaves %s events to process", user_id, len(discovered_list_to_process))

    # Only do 150 events a time so we don't blow up memory
    # TODO(lambert): Maybe do something whereby we don't load fb-events for things we just need to add a source-id on, and only load for things without a potential-event at all. Will need to change the make_potential_event_with_source() API around though...perhaps it's about time.
    if len(event_ids) > 150:
        logging.info("Trimming to 150 events so we don't blow through memory, we'll get the rest of the events next time we run...")
        event_ids = sorted(event_ids)[:150]

    logging.info("Going to look up %s events", len(event_ids))

    event_pipeline.process_discovered_events(fbl, discovered_list)

