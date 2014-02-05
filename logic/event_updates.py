import datetime
import logging

from events import eventdata
import fb_api
import geohash
import locations
from logic import event_classifier
from logic import event_locations
from logic import search
from util import dates

def _event_time_period(db_event):
    if not db_event.start_time:
        return None
    event_end_time = dates.faked_end_time(db_event.start_time, db_event.end_time)
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    event_relative = (event_end_time - today).total_seconds()
    if event_relative > 0:
        return eventdata.TIME_FUTURE
    else:
        return eventdata.TIME_PAST

# Even if the fb_event isn't updated, sometimes we still need to force a db_event update
def need_forced_update(db_event):
    # If the expected time period is not the same as what we've computed and stored, we need to force update
    new_time_period = (db_event.search_time_period != _event_time_period(db_event))
    return new_time_period

def update_and_save_event(db_event, fb_dict):
    _inner_make_event_findable_for(db_event, fb_dict)
    search.update_fulltext_search_index(db_event, fb_dict)

def _inner_make_event_findable_for(db_event, fb_dict):
    # set up any cached fields or bucketing or whatnot for this event

    if fb_dict['empty'] == fb_api.EMPTY_CAUSE_DELETED:
        db_event.start_time = None
        db_event.end_time = None
        db_event.search_time_period = None
        db_event.address = None
        db_event.actual_city_name = None
        db_event.city_name = None
        return
    elif fb_dict['empty'] == fb_api.EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS:
        # TODO(lambert): Find a better way to solve this hack
        # Where insufficient-access events don't get re-processed,
        # and don't pass into TIME_PAST
        db_event.search_time_period = _event_time_period(db_event)
        return

    if 'owner' in fb_dict['info']:
        db_event.owner_fb_uid = fb_dict['info']['owner']['id']
    else:
        db_event.owner_fb_uid = None

    db_event.start_time = dates.parse_fb_start_time(fb_dict)
    db_event.end_time = dates.parse_fb_end_time(fb_dict)
    db_event.search_time_period = _event_time_period(db_event)

    location_info = event_locations.LocationInfo(fb_dict, db_event=db_event)
    # If we got good values from before, don't overwrite with empty values!
    if location_info.actual_city() or not db_event.actual_city_name:
        db_event.anywhere = location_info.is_online_event()
        db_event.actual_city_name = location_info.actual_city()
        db_event.city_name = location_info.largest_nearby_city()
        if db_event.actual_city_name:
            db_event.latitude, db_event.longitude = location_info.latlong()
            db_event.geohashes = []
            for x in range(locations.max_geohash_bits):
                db_event.geohashes.append(str(geohash.Geostring((db_event.latitude, db_event.longitude), depth=x)))
        else:
            db_event.latitude = None
            db_event.longitude = None
            db_event.geohashes = []
            #TODO(lambert): find a better way of reporting/notifying about un-geocodeable addresses
            logging.warning("No geocoding results for eid=%s is: %s", db_event.fb_event_id, location_info)

    db_event.event_keywords = event_classifier.relevant_keywords(fb_dict)
