import logging

from google.appengine.ext import deferred

import fb_api
from events import eventdata
from events import event_locations
from events import event_updates
from logic import pubsub
from nlp import event_classifier
from . import potential_events
from . import thing_db

# valid parameters for creating_method= argument below
CM_AUTO = 'CM_AUTO'
CM_ADMIN = 'CM_ADMIN'
CM_USER = 'CM_USER'

class AddEventException(Exception):
    pass

def add_update_event(event_id, user_id, fbl, remapped_address=None, override_address=None, creating_method=None):
    fbl.request(fb_api.LookupEvent, event_id, allow_cache=False)
    #DISABLE_ATTENDING
    #fbl.request(fb_api.LookupEventAttending, event_id, allow_cache=False)
    fbl.batch_fetch()

    fb_event = fbl.fetched_data(fb_api.LookupEvent, event_id)
    #DISABLE_ATTENDING
    fb_event_attending = None
    #fb_event_attending = fbl.fetched_data(fb_api.LookupEventAttending, event_id)
    if not fb_api.is_public_ish(fb_event):
        raise AddEventException('Cannot add secret/closed events to dancedeets!')

    if remapped_address is not None:
        event_locations.update_remapped_address(fb_event, remapped_address)

    e = eventdata.DBEvent.get_or_insert(event_id)
    newly_created = (e.creating_fb_uid is None)
    if override_address is not None:
        e.address = override_address
    #STR_ID_MIGRATE
    e.creating_fb_uid = long(user_id) if user_id else None
    if creating_method:
        e.creating_method = creating_method
    event_updates.update_and_save_event(e, fb_event)
    thing_db.create_source_from_event(fbl, e)

    if newly_created:
        logging.info("New event, publishing to twitter/facebook")
        deferred.defer(pubsub.eventually_publish_event, fbl, e.fb_event_id)

    potential_event = potential_events.make_potential_event_without_source(event_id, fb_event, fb_event_attending)
    classified_event = event_classifier.get_classified_event(fb_event, potential_event.language)
    if potential_event:
        for source_id in potential_event.source_ids:
            #STR_ID_MIGRATE
            source_id = str(source_id)
            thing_db.increment_num_real_events(source_id)
            if not classified_event.is_dance_event():
                thing_db.increment_num_false_negatives(source_id)
    # Hmm, how do we implement this one?# thing_db.increment_num_real_events_without_potential_events(source_id)
    return fb_event, e
