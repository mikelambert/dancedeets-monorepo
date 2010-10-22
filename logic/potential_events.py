from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from events import eventdata
import fb_api
from logic import event_classifier

class PotentialEvent(db.Model):
    looked_at = db.BooleanProperty()

def save_potential_fb_events(new_dance_events):
    for event in new_dance_events:
        pe = PotentialEvent.get_or_insert(str(event['info']['id']))
        # saves it, with potentially false 'looked_at' field (unless already set as true by myself)
        if pe.looked_at is None:
            pe.looked_at = False
            try:
                pe.put()
            except apiproxy_errors.CapabilityDisabledError:
                pass

def get_potential_dance_events(batch_lookup, user):
    results_json = batch_lookup.data_for_user(user.fb_uid)['all_event_info']
    events = sorted(results_json, key=lambda x: x['start_time'])
    second_batch_lookup = fb_api.CommonBatchLookup(batch_lookup.fb_uid, batch_lookup.fb_graph)
    for mini_fb_event in events:
        second_batch_lookup.lookup_event(str(mini_fb_event['eid']))
    second_batch_lookup.finish_loading()
    dance_event_ids = []
    for mini_fb_event in events:
        fb_event = second_batch_lookup.data_for_event(mini_fb_event['eid'])
        if fb_event['deleted'] or fb_event['info']['privacy'] != 'OPEN':
            continue # only legit events
        is_dance_event = event_classifier.is_dance_event(fb_event)
        if is_dance_event:
            dance_event_ids.append(str(mini_fb_event['eid']))
    # ideally would use keys_only=True, but that's not supported on get_by_key_name :-/
    found_events = eventdata.DBEvent.get_by_key_name(dance_event_ids)
    found_event_ids = [x.key().name() for x in found_events if x]
    new_dance_event_ids = set(dance_event_ids).difference(found_event_ids)
    new_dance_events = [second_batch_lookup.data_for_event(x) for x in new_dance_event_ids]
    new_dance_events = sorted(new_dance_events, key=lambda x: x['info']['start_time'])
    save_potential_fb_events(new_dance_events)
    return new_dance_events

