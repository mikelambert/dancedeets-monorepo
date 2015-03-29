import datetime
import logging

from google.appengine.ext import ndb

import fb_api
from events import eventdata
from loc import gmaps_api
from rankings import rankings
from search import search
from nlp import categories
from nlp import event_classifier
from util import dates
from . import event_locations

def _event_time_period(db_event):
    return dates.event_time_period(db_event.start_time, db_event.end_time)

def delete_event(db_event):
    search.delete_from_fulltext_search_index(db_event.fb_event_id)
    db_event.key.delete()

# Even if the fb_event isn't updated, sometimes we still need to force a db_event update
def need_forced_update(db_event):
    # If the expected time period is not the same as what we've computed and stored, we need to force update
    new_time_period = (db_event.search_time_period != _event_time_period(db_event))
    return new_time_period

def update_and_save_event(db_event, fb_event):
    update_and_save_event_batch([(db_event, fb_event)])

def update_and_save_event_batch(events_to_update, update_geodata=True):
    for db_event, fb_event in events_to_update:
        logging.info("Updating and saving DBEvent %s", db_event.fb_event_id)
        _inner_make_event_findable_for(db_event, fb_event, update_geodata=update_geodata)
    # We want to save it here, no matter how it was changed.
    db_events = [x[0] for x in events_to_update]
    objects_to_put = list(db_events)
    objects_to_put += [eventdata.DisplayEvent.build(x) for x in db_events if eventdata.DisplayEvent.can_build_from(x)]
    ndb.put_multi(objects_to_put)
    search.update_fulltext_search_index_batch(events_to_update)

def _all_attending_count(fb_event):
    # TODO(FB2.0): cleanup!
    data = fb_event.get('fql_info', {}).get('data')
    if data and data[0].get('attending_count'):
        return data[0]['attending_count']
    else:
        if 'info' in fb_event and fb_event['info'].get('invited_count'):
            return fb_event['info']['attending_count']
        else:
            return None


def _inner_make_event_findable_for(db_event, fb_dict, update_geodata):
    """set up any cached fields or bucketing or whatnot for this event"""

    # Update this event with the latest time_period regardless (possibly overwritten below)
    db_event.search_time_period = _event_time_period(db_event)

    if fb_dict['empty'] == fb_api.EMPTY_CAUSE_DELETED:
        # If this event has already past, don't allow it to be deleted. We want to keep history!
        if db_event.end_time < datetime.datetime.now() - datetime.timedelta(days=2):
            return
        db_event.start_time = None
        db_event.end_time = None
        db_event.search_time_period = None
        db_event.address = None
        db_event.actual_city_name = None
        db_event.city_name = None
        db_event.fb_event = fb_dict
        return
    elif fb_dict['empty'] == fb_api.EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS:
        db_event.search_time_period = _event_time_period(db_event)
        # Don't copy the fb_event over, or any of its fields
        return

    # Screw db-normalized form, store this here (and location_geocode down below)
    db_event.fb_event = fb_dict
    if 'owner' in fb_dict['info']:
        db_event.owner_fb_uid = fb_dict['info']['owner']['id']
    else:
        db_event.owner_fb_uid = None

    db_event.attendee_count = _all_attending_count(fb_dict)

    db_event.start_time = dates.parse_fb_start_time(fb_dict)
    db_event.end_time = dates.parse_fb_end_time(fb_dict)
    db_event.search_time_period = _event_time_period(db_event)

    db_event.event_keywords = event_classifier.relevant_keywords(fb_dict)
    db_event.auto_categories = [x.index_name for x in categories.find_styles(fb_dict)]

    if update_geodata:
        # Don't use cached/stale geocode when constructing the LocationInfo here
        db_event.location_geocode = None
        location_info = event_locations.LocationInfo(fb_dict, db_event=db_event)

        # If we got good values from before, don't overwrite with empty values!
        if location_info.actual_city() != db_event.actual_city_name or not db_event.actual_city_name:
            db_event.anywhere = location_info.is_online_event()
            db_event.actual_city_name = location_info.actual_city()
            if location_info.geocode:
                db_event.city_name = rankings.get_ranking_location_latlng(location_info.geocode.latlng())
            else:
                db_event.city_name = "Unknown"
            if db_event.actual_city_name:
                db_event.latitude, db_event.longitude = location_info.latlong()
            else:
                db_event.latitude = None
                db_event.longitude = None
                #TODO(lambert): find a better way of reporting/notifying about un-geocodeable addresses
                logging.warning("No geocoding results for eid=%s is: %s", db_event.fb_event_id, location_info)

        # This only grabs the very first result from the raw underlying geocode request, since that's all that's used to construct the Geocode object in memory
        db_event.location_geocode = gmaps_api.convert_geocode_to_json(location_info.geocode)

        db_event.country = location_info.geocode.country() if location_info.geocode else None
    else:
        db_event.country = db_event.get_geocode().country() if db_event.has_geocode() else None
