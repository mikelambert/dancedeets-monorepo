import logging

import fb_api
from . import event_pipeline
from . import potential_events
from . import thing_db


def get_potential_dance_events(fbl, user_id, fb_user_events):
    results_json = fb_api.LookupUserEvents.all_events(fb_user_events)

    event_ids = [x['id'] for x in sorted(results_json, key=lambda x: x.get('start_time'))]

    logging.info("For user id %s, found %s invited events %s", user_id, len(event_ids), event_ids)

    source = thing_db.create_source_from_id(fbl, user_id)
    source.put()

    discovered_list = [potential_events.DiscoveredEvent(x, source, thing_db.FIELD_INVITES) for x in event_ids]

    logging.info("Going to filter-and-lookup %s events", len(discovered_list))

    event_pipeline.process_discovered_events(fbl, discovered_list)
