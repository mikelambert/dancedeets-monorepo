import logging

from google.appengine.ext import deferred

import fb_api
from events import eventdata
from events import event_locations
from events import event_updates
from pubsub import pubsub
from nlp import event_classifier
from . import potential_events
from . import thing_db

class AddEventException(Exception):
    pass

def add_update_event(fb_event, fbl, creating_uid=None, visible_to_fb_uids=None, remapped_address=None, override_address=None, creating_method=None):
    if not fb_api.is_public_ish(fb_event):
        raise AddEventException('Cannot add secret/closed events to dancedeets!')

    if remapped_address is not None:
        event_locations.update_remapped_address(fb_event, remapped_address)

    e = eventdata.DBEvent.get_or_insert(fb_event['info']['id'])
    newly_created = (e.creating_fb_uid is None)
    if override_address is not None:
        e.address = override_address
    if newly_created and creating_method:
        e.creating_method = creating_method
        # Don't override the original creating_fb_uid
        #STR_ID_MIGRATE
        e.creating_fb_uid = long(creating_uid) if creating_uid else None

    if visible_to_fb_uids is None:
        if creating_uid is not None:
            visible_to_fb_uids = [creating_uid]
        else:
            visible_to_fb_uids = []
    e.visible_to_fb_uids = visible_to_fb_uids

    # Updates and saves the event
    event_updates.update_and_save_fb_events([(e, fb_event)])

    if newly_created:
        logging.info("New event, publishing to twitter/facebook")
        deferred.defer(pubsub.eventually_publish_event, e.fb_event_id)

    fbl.clear_local_cache()
    deferred.defer(crawl_event_source, fbl, e.fb_event_id)

    # like the fb page?
    deferred.defer(like_event_admin_pages, e.fb_event_id)

    return e


def crawl_event_source(fbl, event_id):
    fb_event = fbl.get(fb_api.LookupEvent, event_id)
    e = eventdata.DBEvent.get_by_id(fb_event['info']['id'])
    thing_db.create_source_from_event(fbl, e)

    # DISABLE_ATTENDING
    fb_event_attending = None
    potential_event = potential_events.make_potential_event_without_source(e.fb_event_id, fb_event, fb_event_attending)
    classified_event = event_classifier.get_classified_event(fb_event, potential_event.language)
    if potential_event:
        for source_id in potential_event.source_ids:
            # STR_ID_MIGRATE
            source_id = str(source_id)
            s = thing_db.Source.get_by_key_name(source_id)
            if not s:
                logging.warning("Couldn't find source %s when updating event %s", source_id, e.fb_event_id)
                continue
            # TODO(lambert): doesn't handle the case of the match score increasing from <0 to >0 in the future
            if not classified_event.is_dance_event():
                s.num_false_negatives = (s.num_false_negatives or 0) + 1
            s.num_real_events = (s.num_real_events or 0) + 1
            s.put()


def like_event_admin_pages(db_event_id):
    db_event = eventdata.DBEvent.get_by_id(db_event_id)
    logging.info("Liking the admin's posts about event %s", db_event.id)
    if not db_event.is_fb_event:
        logging.info("Event is not FB event")
        return
    if not db_event.public:
        logging.info("Event is not public")
        return
    fbl = pubsub.get_dancedeets_fbl()
    if not fbl:
        logging.error("Failed to find DanceDeets page access token.")
        return
    for admin in db_event.admins:
        logging.info('Liking wall posts for admin %s (%s)', admin['id'], admin['name'])
        result_feed = fbl.fb.get('v2.5/%s/feed' % admin['id'], {'fields': 'link'})
        if result_feed.get('error'):
            logging.error("Could not find event %s's admin with id %s: %s", db_event_id, admin['id'], result_feed['error'])
            continue
        for item in result_feed['data']:
            logging.info('Found link to %s', item.get('link', ''))
            if '/events/%s' % db_event.fb_event_id in item.get('link', ''):
                logging.info('Liking post with id %s', item['id'])
                result = fbl.fb.post('v2.5/%s/likes' % item['id'], None, {})
                if 'error' in result:
                    logging.error("Post 'like' returned: %s", result)
                else:
                    logging.info("Post 'like' returned: %s", result)
