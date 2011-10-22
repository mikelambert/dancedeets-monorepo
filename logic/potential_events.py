import logging

from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from events import eventdata
import fb_api
from logic import event_classifier
from logic import thing_db
from util import properties

class PotentialEvent(db.Model):
    fb_event_id = property(lambda x: int(x.key().name()))

    looked_at = db.BooleanProperty()
    match_score = db.IntegerProperty()

    # need to delete these
    source = db.StringProperty()
    source_ids = db.ListProperty(int)
    source_fields = db.ListProperty(str)


def make_potential_event_with_source(fb_event_id, match_score, source_id, source_field):
    def _internal_add_source_for_event_id():
        potential_event = PotentialEvent.get_by_key_name(str(fb_event_id)) or PotentialEvent(key_name=str(fb_event_id))
        # If already added, return
        has_source = False
        for source_id_, source_field_ in zip(potential_event.source_ids, potential_event.source_fields):
            if source_id_ == source_id and source_field_ == source_field:
                has_source = True
        
        if has_source and potential_event.match_score == match_score:
            return False
        potential_event.source_ids.append(source_id)
        potential_event.source_fields.append(source_field)
        potential_event.match_score = match_score
        potential_event.put()
        return True

    new_source = False
    try:
        new_source = db.run_in_transaction(_internal_add_source_for_event_id)
    except apiproxy_errors.CapabilityDisabledError, e:
        logging.error("Error saving potential event %s due to %s", event_id, e)
    if new_source:
        thing_db.increment_num_potential_events(source_id)

def get_potential_dance_events(batch_lookup, user_id):
    try:
        results_json = batch_lookup.data_for_user_events(user_id)['all_event_info']
        events = sorted(results_json, key=lambda x: x.get('start_time'))
    except fb_api.NoFetchedDataException:
        events = []
    second_batch_lookup = batch_lookup.copy()
    for mini_fb_event in events:
        second_batch_lookup.lookup_event(str(mini_fb_event['eid']))
    second_batch_lookup.finish_loading()
    dance_event_ids = []
    match_scores = {}
    for mini_fb_event in events:
        event_id = str(mini_fb_event['eid'])
        try:
            fb_event = second_batch_lookup.data_for_event(event_id)
        except fb_api.NoFetchedDataException:
            continue # must be a non-saved event, probably due to private/closed event. so ignore.
        if fb_event['deleted'] or fb_event['info']['privacy'] != 'OPEN':
            continue # only legit events
        #TODO(lambert): before we fix this to be a smarter classifier, perhaps we should do better caching of the results to avoid blowing quotas
        classified_event = event_classifier.get_classified_event(fb_event)
        if classified_event.is_dance_event():
            dance_event_ids.append(event_id)
            match_scores[event_id] = classified_event.match_score()
    # TODO(lambert): ideally would use keys_only=True, but that's not supported on get_by_key_name :-(

    # Filter out DBEvents
    found_events = eventdata.DBEvent.get_by_key_name(dance_event_ids)
    found_event_ids = [x.fb_event_id for x in found_events if x]
    new_dance_event_ids = set(dance_event_ids).difference(found_event_ids)

    # Filter out looked_at PotentialEvents
    potential_events = PotentialEvent.get_by_key_name(new_dance_event_ids)
    seen_potential_event_ids = [x.fb_event_id for x in potential_events if x and x.looked_at]
    new_unseen_dance_event_ids = set(new_dance_event_ids).difference(seen_potential_event_ids)

    new_dance_events = [second_batch_lookup.data_for_event(x) for x in new_unseen_dance_event_ids]
    source = thing_db.create_source_for_id(user_id, fb_data=None)
    source.put()
    for event_id in new_unseen_dance_event_ids:
        make_potential_event_with_source(event_id, match_scores[event_id], source_id=source.graph_id, source_field=thing_db.FIELD_INVITES)
    new_dance_events = sorted(new_dance_events, key=lambda x: x['info'].get('start_time'))
    return new_dance_events
