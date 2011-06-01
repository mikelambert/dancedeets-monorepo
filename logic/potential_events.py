import logging

from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from events import eventdata
import fb_api
from logic import event_classifier

class PotentialEvent(db.Model):
    looked_at = db.BooleanProperty()
    source = db.StringProperty()

SOURCE_USER_INVITES = 'user_invites'
SOURCE_POSTS = 'posts'

def source_from_user_invites(user_id):
    return '%s:%s' % (SOURCE_USER_INVITES, user_id)

def source_from_posts(thing_id):
    return '%s:%s' % (SOURCE_POSTS, thing_id)

def display_for_source(source_str):
    source_type, source_id = source_str.split(':', 1)
    return "<a href="http://ww.facebook.com/profile.php?id=%(source_id)s>%(source_type)s from %(source_id)s</a>" % dict(source_id=source_id, source_type=source_type)

def save_potential_fb_event_ids_if_new(event_ids, source=None):
    filtered_ids = [x for x in event_ids if not eventdata.DBEvent.get_by_key_name(str(x)) and not PotentialEvent.get_by_key_name(str(x))]
    save_potential_fb_event_ids(filtered_ids, source=source)

def save_potential_fb_event_ids(event_ids, source=None):
    for event_id in event_ids:
        try:
            logging.info("Saving potential event %s", event_id)
            pe = PotentialEvent.get_or_insert(str(event_id))
            # saves it, with potentially false 'looked_at' field (unless already set as true by myself)
            if pe.looked_at is None:
                pe.looked_at = False
                pe.source = source
                pe.put()
        except apiproxy_errors.CapabilityDisabledError:
            pass

def get_potential_dance_events(batch_lookup, user_id):
    try:
        results_json = batch_lookup.data_for_user_events(user_id)['all_event_info']
        events = sorted(results_json, key=lambda x: x['start_time'])
    except fb_api.NoFetchedDataException:
        events = []
    second_batch_lookup = fb_api.CommonBatchLookup(batch_lookup.fb_uid, batch_lookup.fb_graph)
    for mini_fb_event in events:
        second_batch_lookup.lookup_event(str(mini_fb_event['eid']))
    second_batch_lookup.finish_loading()
    dance_event_ids = []
    for mini_fb_event in events:
        try:
            fb_event = second_batch_lookup.data_for_event(mini_fb_event['eid'])
        except fb_api.NoFetchedDataException:
            continue # must be a non-saved event, probably due to private/closed event. so ignore.
        if fb_event['deleted'] or fb_event['info']['privacy'] != 'OPEN':
            continue # only legit events
        #TODO(lambert): before we fix this to be a smarter classifier, perhaps we should do better caching of the results to avoid blowing quotas
        is_dance_event = event_classifier.is_dance_event(fb_event)
        if is_dance_event:
            dance_event_ids.append(str(mini_fb_event['eid']))
    # ideally would use keys_only=True, but that's not supported on get_by_key_name :-/

    # Filter out DBEvents
    found_events = eventdata.DBEvent.get_by_key_name(dance_event_ids)
    found_event_ids = [x.key().name() for x in found_events if x]
    new_dance_event_ids = set(dance_event_ids).difference(found_event_ids)

    # Filter out looked_at PotentialEvents
    potential_events = PotentialEvent.get_by_key_name(new_dance_event_ids)
    seen_potential_event_ids = [x.key().name() for x in potential_events if x and x.looked_at]
    new_unseen_dance_event_ids = set(new_dance_event_ids).difference(seen_potential_event_ids)

    new_dance_events = [second_batch_lookup.data_for_event(x) for x in new_unseen_dance_event_ids]
    save_potential_fb_event_ids(new_unseen_dance_event_ids, source=source_from_user_invites(user_id))
    new_dance_events = sorted(new_dance_events, key=lambda x: x['info']['start_time'])
    return new_dance_events
