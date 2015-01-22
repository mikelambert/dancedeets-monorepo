from google.appengine.ext import deferred


import fb_api
import logging
from logic import potential_events
from logic import thing_db

def function_migrate_thing_to_new_id(fbapi_obj, old_source_id, new_source_id):
    old_source = thing_db.Source.get_by_key_name(old_source_id)

    # Maybe we got two of these and it already ran in parallel, so ignore this one
    if not old_source:
        return

    key = (fb_api.LookupThingFeed, new_source_id)

    fbapi_obj.raise_on_page_redirect = True
    try:
        results = fbapi_obj.fetch_keys([key])
    except fb_api.PageRedirectException as e:
        # If our forwarding address in turn has its own forwarding address,
        # repoint the old thing further down the chain
        deferred.defer(function_migrate_thing_to_new_id, fbapi_obj, old_source_id, e.to_id)
        return

    thing_feed = results[key]

    new_source = thing_db.create_source_for_id(new_source_id, thing_feed)
    new_source.creating_fb_uid = new_source.creating_fb_uid or old_source.creating_fb_uid
    new_source.creation_time = new_source.creation_time or old_source.creation_time
    new_source.last_scrape_time = new_source.last_scrape_time or old_source.last_scrape_time

    new_source.num_all_events = (new_source.num_all_events or 0) + (old_source.num_all_events or 0)
    new_source.num_potential_events = (new_source.num_potential_events or 0) + (old_source.num_potential_events or 0)
    new_source.num_real_events = (new_source.num_real_events or 0) + (old_source.num_real_events or 0)
    new_source.num_false_negatives = (new_source.num_false_negatives or 0) + (old_source.num_false_negatives or 0)

    # Who has pointers to sources??
    migrate_potential_events(int(old_source_id), int(new_source_id))

    new_source.put()
    old_source.delete()

def migrate_potential_events(old_source_id, new_source_id):
    potential_event_list = potential_events.PotentialEvent.gql("WHERE source_ids = %s" % old_source_id).fetch(100)

    for pe in potential_event_list:
        logging.info("old pe %s has ids: %s", pe.fb_event_id, pe.source_ids)
        source_infos = set()
        for source_info in zip(pe.source_ids, pe.source_fields):
            print source_info[0], old_source_id, type(source_info[0]), type(old_source_id)
            if source_info[0] == long(old_source_id):
                source_info = (long(new_source_id), source_info[1])
            source_infos.add(source_info)
        source_infos_list = list(source_infos)
        pe.source_ids = [x[0] for x in source_infos_list]
        pe.source_fields = [x[1] for x in source_infos_list]
        logging.info("new pe %s has ids: %s", pe.fb_event_id, pe.source_ids)
        pe.put()

    if len(potential_event_list):
        # Tail recursion via task queues!
        deferred.defer(migrate_potential_events, old_source_id, new_source_id)

