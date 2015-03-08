import logging

import fb_api
from event_scraper import potential_events
from event_scraper import auto_add

def process_event_ids(fbl, event_ids, source, source_field):

    #for each fb_event, create potential event, set match score
    #for each fb event, if potential event, run autoclassifier
    #if good, add

    fb_events = fbl.get_multi(fb_api.LookupEvent, event_ids)

    filtered_pe_events = []
    filtered_fb_events = []
    for fb_event in fb_events:
        if not fb_event:
            continue
        event_id = fb_event['info']['id']
        if fb_event['empty'] or not fb_api.is_public_ish(fb_event):
            logging.info("event id %s: deleted, or private", event_id)
            continue # only legit events
        # makes a potential event, with scored information. transactions. one. by. one.
        discovered = potential_events.DiscoveredEvent(event_id, source, source_field)
        pe_event = potential_events.make_potential_event_with_source(fb_event, discovered)
        filtered_pe_events.append(pe_event)
        filtered_fb_events.append(fb_event)
    # TODO: Create new sources, update source feed values, etc? done in make_potential_events_with_source, but need more that's not done there

    logging.info("Going to classify the %s potential events", len(event_ids))
    # Classify events on the fly as we add them as potential events, instead of waiting for the mapreduce
    auto_add.classify_events(fbl, filtered_pe_events, filtered_fb_events)
