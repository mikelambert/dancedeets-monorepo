import logging

from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from events import eventdata
from logic import event_updates
from logic import gprediction
from logic import gtranslate
from event_scraper import thing_db
from nlp import event_classifier
from util import dates

class PotentialEvent(db.Model):
    fb_event_id = property(lambda x: str(x.key().name()))

    language = db.StringProperty()
    looked_at = db.BooleanProperty()
    auto_looked_at = db.BooleanProperty()
    dance_bias_score = db.FloatProperty()
    non_dance_bias_score = db.FloatProperty()
    match_score = db.IntegerProperty()
    show_even_if_no_score = db.BooleanProperty()
    should_look_at = db.BooleanProperty()

    #STR_ID_MIGRATE
    source_ids = db.ListProperty(int)
    source_fields = db.ListProperty(str)

    # This is a representation of FUTURE vs PAST, so we can filter in our mapreduce criteria for relevant future events easily
    past_event = db.BooleanProperty()

    def has_source_with_field(self, source_id, source_field):
        has_source = False
        for source_id_, source_field_ in zip(self.source_ids, self.source_fields):
            #STR_ID_MIGRATE
            source_id_ = str(source_id_)
            if source_id_ == source_id and source_field_ == source_field:
                has_source = True
        return has_source

    def put(self):
        #TODO(lambert): write as pre-put hook once we're using NDB.
        self.should_look_at = bool(self.match_score > 0 or self.show_even_if_no_score)
        super(PotentialEvent, self).put()

    def set_past_event(self, fb_event):
        if not fb_event:
            past_event = True
        elif fb_event['empty']:
            past_event = True
        else:
            start_time = dates.parse_fb_start_time(fb_event)
            end_time = dates.parse_fb_end_time(fb_event)
            past_event = (eventdata.TIME_PAST == event_updates._event_time_period2(start_time, end_time))
        changed = (self.past_event != past_event)
        self.past_event = past_event
        return changed


def get_language_for_fb_event(fb_event):
    return gtranslate.check_language('%s. %s' % (
        fb_event['info'].get('name', ''),
        fb_event['info'].get('description', '')
    ))

def _common_potential_event_setup(potential_event, fb_event):
    # only calculate the event score if we've got some new data (new source, etc)
    # TODO(lambert): implement a mapreduce over future-event potential-events that recalculates scores
    # Turn off translation and prediction since they're too expensive for me. :(
    #if not potential_event.language:
    #    potential_event.language = get_language_for_fb_event(fb_event)
    match_score = event_classifier.get_classified_event(fb_event, language=potential_event.language).match_score()
    potential_event.match_score = match_score
    potential_event.set_past_event(fb_event)

def update_scores_for_potential_event(potential_event, fb_event, fb_event_attending, service=None):
    return potential_event # This prediction isn't really working, so let's turn it off for now
    if potential_event and not getattr(potential_event, 'dance_bias_score'):
        predict_service = service or gprediction.get_predict_service()
        dance_bias_score, non_dance_bias_score = gprediction.predict(potential_event, fb_event, fb_event_attending, service=predict_service)
        fb_event_id = potential_event.fb_event_id
        def _internal_update_scores():
            potential_event = PotentialEvent.get_by_key_name(fb_event_id)
            potential_event.dance_bias_score = dance_bias_score
            potential_event.non_dance_bias_score = non_dance_bias_score
            potential_event.put()
            return potential_event
        try:
            potential_event = db.run_in_transaction(_internal_update_scores)
        except apiproxy_errors.CapabilityDisabledError, e:
            logging.error("Error saving potential event %s due to %s", fb_event_id, e)
    return potential_event


def make_potential_event_without_source(fb_event_id, fb_event, fb_event_attending):
    def _internal_add_potential_event():
        potential_event = PotentialEvent.get_by_key_name(fb_event_id)
        if not potential_event:
            potential_event = PotentialEvent(key_name=fb_event_id)
            # TODO(lambert): this may re-duplicate this work for potential events that already exist. is this okay or not?
            _common_potential_event_setup(potential_event, fb_event)
            potential_event.put()
        return potential_event
    try:
        potential_event = db.run_in_transaction(_internal_add_potential_event)
    except apiproxy_errors.CapabilityDisabledError, e:
        logging.error("Error saving potential event %s due to %s", fb_event_id, e)

    potential_event = update_scores_for_potential_event(potential_event, fb_event, fb_event_attending)
    return potential_event

def make_potential_event_with_source(fb_event_id, fb_event, fb_event_attending, source, source_field):
    # show all events from a source if enough of them slip through our automatic filters
    show_all_events = source.fraction_real_are_false_negative() > 0.05 and source_field != thing_db.FIELD_INVITES # never show all invites, privacy invasion
    def _internal_add_source_for_event_id():
        potential_event = PotentialEvent.get_by_key_name(fb_event_id) or PotentialEvent(key_name=fb_event_id)
        # If already added, return
        if potential_event.has_source_with_field(source.graph_id, source_field):
            return False, potential_event.match_score

        _common_potential_event_setup(potential_event, fb_event)

        #STR_ID_MIGRATE
        potential_event.source_ids.append(long(source.graph_id))
        potential_event.source_fields.append(source_field)

        potential_event.show_even_if_no_score = potential_event.show_even_if_no_score or show_all_events
        potential_event.put()
        return True, potential_event.match_score

    new_source = False
    try:
        new_source, match_score = db.run_in_transaction(_internal_add_source_for_event_id)
    except apiproxy_errors.CapabilityDisabledError, e:
        logging.error("Error saving potential event %s due to %s", fb_event_id, e)
    potential_event = PotentialEvent.get_by_key_name(fb_event_id)
    potential_event = update_scores_for_potential_event(potential_event, fb_event, fb_event_attending)
    if new_source:
        #TODO(lambert): doesn't handle the case of the match score increasing from <0 to >0 in the future
        if match_score > 0:
            thing_db.increment_num_potential_events(source.graph_id)
        thing_db.increment_num_all_events(source.graph_id)
    return potential_event

