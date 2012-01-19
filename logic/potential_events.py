import logging

from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from events import eventdata
import fb_api
from logic import event_classifier
from logic import gprediction
from logic import gtranslate
from logic import thing_db
from util import properties

class PotentialEvent(db.Model):
    fb_event_id = property(lambda x: int(x.key().name()))

    language = db.StringProperty()
    looked_at = db.BooleanProperty()
    dance_prediction_score = db.FloatProperty()
    match_score = db.IntegerProperty()
    show_even_if_no_score = db.BooleanProperty()

    source_ids = db.ListProperty(int)
    source_fields = db.ListProperty(str)

def get_language_for_fb_event(fb_event):
    return gtranslate.check_language('%s. %s' % (
        fb_event['info'].get('name', ''),
        fb_event['info'].get('description', '')
    ))

def _common_potential_event_setup(potential_event, fb_event, fb_event_attending, predict_service):
    # only calculate the event score if we've got some new data (new source, etc)
    # TODO(lambert): implement a mapreduce over future-event potential-events that recalculates scores
    if not potential_event.language:
        potential_event.language = get_language_for_fb_event(fb_event)
    if not getattr(potential_event, 'dance_prediction_score'):
        potential_event.dance_prediction_score = gprediction.predict(potential_event, fb_event, fb_event_attending, service=predict_service)
    match_score = event_classifier.get_classified_event(fb_event, language=potential_event.language).match_score()
    potential_event.match_score = match_score

def make_potential_event_without_source(fb_event_id, fb_event, fb_event_attending):
    predict_service = gprediction.get_predict_service()
    def _internal_add_potential_event():
        potential_event = PotentialEvent.get_by_key_name(str(fb_event_id))
        if not potential_event:
            potential_event = PotentialEvent(key_name=str(fb_event_id))
            # TODO(lambert): this may re-duplicate this work for potential events that already exist. is this okay or not?
            _common_potential_event_setup(potential_event, fb_event, fb_event_attending, predict_service)
            potential_event.put()
        return potential_event
    try:
        potential_event = db.run_in_transaction(_internal_add_potential_event)
    except apiproxy_errors.CapabilityDisabledError, e:
        logging.error("Error saving potential event %s due to %s", event_id, e)
    return potential_event

def make_potential_event_with_source(fb_event_id, fb_event, fb_event_attending, source, source_field):
    predict_service = gprediction.get_predict_service()
    # show all events from a source if enough of them slip through our automatic filters
    show_all_events = source.fraction_real_are_false_negative() > 0.05 and source_field != thing_db.FIELD_INVITES # never show all invites, privacy invasion
    def _internal_add_source_for_event_id():
        potential_event = PotentialEvent.get_by_key_name(str(fb_event_id)) or PotentialEvent(key_name=str(fb_event_id))
        # If already added, return
        has_source = False
        for source_id_, source_field_ in zip(potential_event.source_ids, potential_event.source_fields):
            if source_id_ == source.graph_id and source_field_ == source_field:
                has_source = True
        
        if has_source:
            return False, potential_event.match_score

        _common_potential_event_setup(potential_event, fb_event, fb_event_attending, predict_service)

        potential_event.source_ids.append(source.graph_id)
        potential_event.source_fields.append(source_field)

        potential_event.show_even_if_no_score = potential_event.show_even_if_no_score or show_all_events
        potential_event.put()
        return True, potential_event.match_score

    new_source = False
    try:
        new_source, match_score = db.run_in_transaction(_internal_add_source_for_event_id)
    except apiproxy_errors.CapabilityDisabledError, e:
        logging.error("Error saving potential event %s due to %s", event_id, e)
    if new_source:
        #TODO(lambert): doesn't handle the case of the match score increasing from <0 to >0 in the future
        if match_score > 0:
            thing_db.increment_num_potential_events(source.graph_id)
        thing_db.increment_num_all_events(source.graph_id)

def get_potential_dance_events(batch_lookup, user_id):
    try:
        results_json = batch_lookup.data_for_user_events(user_id)['all_event_info']['data']
        events = sorted(results_json, key=lambda x: x.get('start_time'))
    except fb_api.NoFetchedDataException:
        events = []
    second_batch_lookup = batch_lookup.copy(allow_cache=True)
    for mini_fb_event in events:
        second_batch_lookup.lookup_event(str(mini_fb_event['eid']))
        second_batch_lookup.lookup_event_attending(str(mini_fb_event['eid']))
    second_batch_lookup.finish_loading()

    source = thing_db.create_source_for_id(user_id, fb_data=None)
    source.put()

    dance_event_ids = []
    for mini_fb_event in events:
        event_id = str(mini_fb_event['eid'])
        try:
            fb_event = second_batch_lookup.data_for_event(event_id)
            fb_event_attending = second_batch_lookup.data_for_event_attending(event_id)
        except fb_api.NoFetchedDataException:
            continue # must be a non-saved event, probably due to private/closed event. so ignore.
        if fb_event['deleted'] or fb_event['info']['privacy'] != 'OPEN':
            continue # only legit events
        make_potential_event_with_source(event_id, fb_event, fb_event_attending, source=source, source_field=thing_db.FIELD_INVITES)
