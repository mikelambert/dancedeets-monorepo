import fb_api
import logging
from util import deferred
from . import potential_events
from . import thing_db

def function_migrate_thing_to_new_id(fbapi_obj, old_source_id, new_source_id):
    old_source = thing_db.Source.get_by_key_name(old_source_id)

    # Maybe we got two of these and it already ran in parallel, so ignore this one
    if not old_source:
        return

    fbl = fb_api.FBLookup(None, fb_api_obj.access_token_list)

    fbl.fb.raise_on_page_redirect = True
    try:
        results = fbl.get(fb_api.LookupThingCommon, new_source_id)
    except fb_api.PageRedirectException as e:
        # If our forwarding address in turn has its own forwarding address,
        # repoint the old thing further down the chain
        deferred.defer(function_migrate_thing_to_new_id, fbl.fb, old_source_id, e.to_id)
        return

    new_source = thing_db.create_source_from_id(fb_api, new_source_id)
    new_source.creating_fb_uid = new_source.creating_fb_uid or old_source.creating_fb_uid
    new_source.creation_time = new_source.creation_time or old_source.creation_time
    new_source.last_scrape_time = new_source.last_scrape_time or old_source.last_scrape_time

    new_source.num_all_events = (new_source.num_all_events or 0) + (old_source.num_all_events or 0)
    new_source.num_potential_events = (new_source.num_potential_events or 0) + (old_source.num_potential_events or 0)
    new_source.num_real_events = (new_source.num_real_events or 0) + (old_source.num_real_events or 0)
    new_source.num_false_negatives = (new_source.num_false_negatives or 0) + (old_source.num_false_negatives or 0)

    # Who has pointers to sources??
    migrate_potential_events(old_source_id, new_source_id)

    new_source.put()
    old_source.delete()

def migrate_potential_events(old_source_id, new_source_id):
    #STR_ID_MIGRATE
    potential_event_list = potential_events.PotentialEvent.gql("WHERE source_ids = %s" % long(old_source_id)).fetch(100)

    for pe in potential_event_list:
        logging.info("old pe %s has ids: %s", pe.fb_event_id, [x.id for x in pe.sources()])
        source_infos = set()
        for source in pe.sources():
            # remap ids
            if source.id == old_source_id:
                #STR_ID_MIGRATE
                source = source.copy()
                source.id = new_source_id
            source_infos.add(source)
        pe.set_sources(source_infos)
        logging.info("new pe %s has ids: %s", pe.fb_event_id, [x.id for x in pe.sources()])
        pe.put()

    if len(potential_event_list):
        # Tail recursion via task queues!
        deferred.defer(migrate_potential_events, old_source_id, new_source_id)

