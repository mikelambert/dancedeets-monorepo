import datetime
import fb_api
from events import eventdata
from logic import event_classifier
from logic import event_locations
from logic import event_updates
from logic import potential_events
from logic import thing_db

class AddEventException(Exception):
    pass

def add_update_event(event_id, user_id, batch_lookup, remapped_address=None, override_address=None, creating_method=None):
    event_id = str(event_id)
    batch_lookup.lookup_event(event_id, allow_cache=False)
    batch_lookup.lookup_event_attending(event_id, allow_cache=False)
    batch_lookup.finish_loading()

    fb_event = batch_lookup.data_for_event(event_id)
    fb_event_attending = batch_lookup.data_for_event_attending(event_id)
    if not fb_api.is_public_ish(fb_event):
        raise AddEventException('Cannot add secret/closed events to dancedeets!')

    if remapped_address is not None:
        event_locations.update_remapped_address(batch_lookup.copy(allow_cache=False), fb_event, remapped_address)

    e = eventdata.DBEvent.get_or_insert(event_id)
    if override_address is not None:
        e.address = override_address
    e.creating_fb_uid = user_id
    if creating_method:
        e.creating_method = creating_method
    e.creation_time = datetime.datetime.now()
    fb_event = batch_lookup.data_for_event(event_id)
    event_updates.update_and_save_event(e, batch_lookup, fb_event)
    thing_db.create_source_from_event(batch_lookup.copy(allow_cache=False), e)

    potential_event = potential_events.make_potential_event_without_source(event_id, fb_event, fb_event_attending)
    classified_event = event_classifier.get_classified_event(fb_event, potential_event.language)
    if potential_event:
        for source_id in potential_event.source_ids:
            thing_db.increment_num_real_events(source_id)
            if not classified_event.is_dance_event():
                thing_db.increment_num_false_negatives(source_id)
    # Hmm, how do we implement this one?# thing_db.increment_num_real_events_without_potential_events(source_id)
    return fb_event, e
