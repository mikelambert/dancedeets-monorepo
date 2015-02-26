import datetime
import logging

import fb_api
from loc import gmaps_api
from rankings import rankings
from search import search
from nlp import event_classifier
from util import dates
from . import eventdata
from . import event_locations

def _event_time_period(db_event):
    return _event_time_period2(db_event.start_time, db_event.end_time)

def _event_time_period2(start_time, end_time):
    if not start_time:
        return None
    event_end_time = dates.faked_end_time(start_time, end_time)
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    event_relative = (event_end_time - today).total_seconds()
    if event_relative > 0:
        return eventdata.TIME_FUTURE
    else:
        return eventdata.TIME_PAST

def delete_event(db_event):
    search.delete_from_fulltext_search_index(db_event.fb_event_id)
    db_event.key.delete()

# Even if the fb_event isn't updated, sometimes we still need to force a db_event update
def need_forced_update(db_event):
    # If the expected time period is not the same as what we've computed and stored, we need to force update
    new_time_period = (db_event.search_time_period != _event_time_period(db_event))
    return new_time_period

def update_and_save_event(db_event, fb_dict):
    _inner_make_event_findable_for(db_event, fb_dict)
    # We want to save it here, no matter how it was changed.
    db_event.put()
    search.update_fulltext_search_index(db_event, fb_dict)


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


def _inner_make_event_findable_for(db_event, fb_dict):
    # set up any cached fields or bucketing or whatnot for this event

    # Screw db-normalized form, store this here (and location_geocode down below)
    db_event.fb_event = fb_dict

    if fb_dict['empty'] == fb_api.EMPTY_CAUSE_DELETED:
        db_event.start_time = None
        db_event.end_time = None
        db_event.search_time_period = None
        db_event.address = None
        db_event.actual_city_name = None
        db_event.city_name = None
        return
    elif fb_dict['empty'] == fb_api.EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS:
        db_event.search_time_period = _event_time_period(db_event)
        return

    if 'owner' in fb_dict['info']:
        db_event.owner_fb_uid = fb_dict['info']['owner']['id']
    else:
        db_event.owner_fb_uid = None

    db_event.attendee_count = _all_attending_count(fb_dict)

    db_event.start_time = dates.parse_fb_start_time(fb_dict)
    db_event.end_time = dates.parse_fb_end_time(fb_dict)
    db_event.search_time_period = _event_time_period(db_event)

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

    db_event.event_keywords = event_classifier.relevant_keywords(fb_dict)

    # This only grabs the very first result from the raw underlying geocode request, since that's all that's used to construct the Geocode object in memory
    db_event.location_geocode = gmaps_api.convert_geocode_to_json(location_info.geocode)
