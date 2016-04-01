import logging

import fb_api
from event_scraper import potential_events
from event_scraper import auto_add


def get_unprocessed_discovered_events(discovered_list):
    discovered_to_process = []
    fb_event_ids = list(set(x.event_id for x in discovered_list))
    potential = potential_events.PotentialEvent.get_by_key_name(fb_event_ids)
    for fb_event_id, pe in zip(fb_event_ids, potential):
        discovered_list_for_event = [x for x in discovered_list if x.event_id == fb_event_id]
        if pe:
            # TODO: Performance Issue!!! O(N*M)
            discovered_to_process.extend([x for x in discovered_list if not pe.has_discovered(x)])
        else:
            discovered_to_process.extend(discovered_list_for_event)
    return discovered_to_process


def process_discovered_events(fbl, full_discovered_list):

    #for each fb_event, create potential event, set match score
    #for each fb event, if potential event, run autoclassifier
    #if good, add

    # TODO(lambert): Maybe filter events for where they're already sourced, before we attempt to load event-attending and recreate it?
    # Not strictly necessary on the invite pipeline, but definitely would be useful on the thing_scraper pipeline

    # Okay, allow the cache here. There are many events we want to load and process, and we can use cached versions, to avoid blowing through our FB quota.
    #TODO(lambert): At some point we need to use cache invalidation to fetch new data and not keep re-processing old data.
    # Also remember this fbl may be used in a mapreduce once we return from this function, so let's not modify it

    discovered_list = get_unprocessed_discovered_events(full_discovered_list)

    logging.info("Filtering out already-discovered-events drops list from %s to %s items.", len(full_discovered_list), len(discovered_list))
    if len(full_discovered_list) < len(discovered_list):
        logging.error('How? Discovered List')
        for i in discovered_list:
            logging.error('%s', i)
        logging.error('Full Discovered List')
        for i in full_discovered_list:
            logging.error('%s', i)

    if not discovered_list:
        return

    orig_allow_cache = fbl.allow_cache
    try:
        fbl.allow_cache = True
        fb_events = fbl.get_multi(fb_api.LookupEvent, [x.event_id for x in discovered_list], allow_fail=True)
    finally:
        fbl.allow_cache = orig_allow_cache

    potential_events_added = []
    for fb_event, discovered in zip(fb_events, discovered_list):
        if not fb_event or fb_event['empty']:
            continue
        event_id = fb_event['info']['id']
        if fb_event['empty'] or not fb_api.is_public_ish(fb_event):
            logging.info("event id %s: deleted, or private", event_id)
            continue # only legit events
        # makes a potential event, with scored information. transactions. one. by. one.
        pe_event = potential_events.make_potential_event_with_source(fb_event, discovered)
        potential_events_added.append(pe_event)
    # TODO: Create new sources, update source feed values, etc? done in make_potential_events_with_source, but need more that's not done there

    fb_lookup = dict((x['info']['id'], x) for x in fb_events if x and not x['empty'])
    pe_lookup = dict((x.fb_event_id, x) for x in potential_events_added)
    potential_event_ids = pe_lookup.keys()
    logging.info("Going to classify the %s potential events", len(discovered_list))
    # Classify events on the fly as we add them as potential events, instead of waiting for the mapreduce
    auto_add.classify_events(fbl, [pe_lookup[x] for x in potential_event_ids], [fb_lookup[x] for x in potential_event_ids])
