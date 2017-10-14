import datetime
import dateutil
import logging
import pytz
import re
import time
from timezonefinder import TimezoneFinder

from google.appengine.ext import ndb

from dancedeets import fb_api
from dancedeets.event_attendees import event_attendee_classifier
from dancedeets.event_attendees import person_city
from dancedeets.loc import gmaps_api
from dancedeets.rankings import cities_db
from dancedeets.search import search
from dancedeets.nlp import categories
from dancedeets.nlp import event_classifier
from dancedeets.util import dates
from dancedeets.util import language
from dancedeets.util import timelog
from . import event_image
from . import event_locations

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATETIME_FORMAT_TZ = "%Y-%m-%dT%H:%M:%S%z"

timezone_finder = TimezoneFinder()


def _event_time_period(db_event):
    return dates.event_time_period(db_event.start_time, db_event.end_time)


def delete_event(db_event):
    search.delete_from_fulltext_search_index(db_event.id)
    db_event.key.delete()
    display_event = search.DisplayEvent.get_by_id(db_event.id)
    if display_event:
        display_event.key.delete()


# Even if the fb_event isn't updated, sometimes we still need to force a db_event update
def need_forced_update(db_event):
    # If the expected time period is not the same as what we've computed and stored, we need to force update
    new_time_period = (db_event.search_time_period != _event_time_period(db_event))
    logging.info(
        "Event %s with time %s - %s: has search_time_period %s, expecting %s", db_event.id, db_event.start_time, db_event.end_time,
        db_event.search_time_period, _event_time_period(db_event)
    )
    return new_time_period


def update_and_save_fb_events(events_to_update, disable_updates=None):
    for db_event, fb_event, fb_event_attending_maybe in events_to_update:
        logging.info("Updating and saving DBEvent fb event %s", db_event.id)
        _inner_make_event_findable_for_fb_event(db_event, fb_event, fb_event_attending_maybe, disable_updates=disable_updates)
    # We want to save it here, no matter how it was changed.
    db_events = [x[0] for x in events_to_update]
    _save_events(db_events, disable_updates=disable_updates)


def update_and_save_web_events(events_to_update, disable_updates=None):
    for db_event, web_event in events_to_update:
        logging.info("Updating and saving DBEvent web event %s", db_event.id)
        _inner_make_event_findable_for_web_event(db_event, web_event, disable_updates=disable_updates)
    db_events = [x[0] for x in events_to_update]
    _save_events(db_events, disable_updates=disable_updates)


def resave_display_events(db_events):
    display_events = [search.DisplayEvent.build(x) for x in db_events]
    ndb.put_multi([x for x in display_events if x])


def _save_events(db_events, disable_updates=None):
    objects_to_put = list(db_events)
    objects_to_put += [search.DisplayEvent.build(x) for x in db_events]
    # Because some DisplayEvent.build() calls return None (from errors, or from inability)
    objects_to_put = [x for x in objects_to_put if x]
    ndb.put_multi(objects_to_put)
    if 'index' not in (disable_updates or []):
        search.update_fulltext_search_index_batch(db_events)


def _all_attending_count(fb_event):
    if 'info' in fb_event and fb_event['info'].get('attending_count'):
        return fb_event['info']['attending_count']
    else:
        return None


def _inner_cache_photo(db_event):
    if db_event.full_image_url:
        try:
            width, height = event_image.cache_image_and_get_size(db_event)
            db_event.json_props['photo_width'] = width
            db_event.json_props['photo_height'] = height
        except (event_image.DownloadError, event_image.NotFoundError, Exception) as e:
            logging.warning('Error downloading flyer for event %s: %r', db_event.id, e)
    else:
        if 'photo_width' in db_event.json_props:
            del db_event.json_props['photo_width']
        if 'photo_height' in db_event.json_props:
            del db_event.json_props['photo_height']


def _inner_make_event_findable_for_fb_event(db_event, fb_dict, fb_event_attending_maybe, disable_updates):
    """set up any cached fields or bucketing or whatnot for this event"""

    # Update this event with the latest time_period regardless (possibly overwritten below)
    db_event.search_time_period = _event_time_period(db_event)

    if fb_dict['empty'] == fb_api.EMPTY_CAUSE_DELETED:
        # If this event has already past, don't allow it to be deleted. We want to keep history!
        if db_event.end_time and db_event.end_time < datetime.datetime.now() - datetime.timedelta(days=2):
            return
        # If we don't have a db_event.end_time, then we've got something messed up, so let's delete the event
        db_event.start_time = None
        db_event.end_time = None
        db_event.search_time_period = None
        db_event.address = None
        db_event.actual_city_name = None
        db_event.city_name = None
        db_event.attendee_geoname_id = None
        db_event.nearby_geoname_id = None
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
    # This assumes db_event.fb_event was set up above...and we then use our accessor
    db_event.admin_fb_uids = [x['id'] for x in db_event.admins]

    db_event.attendee_count = _all_attending_count(fb_dict)

    db_event.start_time = dates.parse_fb_start_time(fb_dict)
    db_event.end_time = dates.parse_fb_end_time(fb_dict)
    db_event.search_time_period = _event_time_period(db_event)

    db_event.event_keywords = event_classifier.relevant_keywords(fb_dict)
    db_event.auto_categories = [x.index_name for x in categories.find_styles(fb_dict) + categories.find_event_types(fb_dict)]

    _inner_common_setup(db_event, disable_updates=disable_updates)

    if 'regeocode' not in (disable_updates or []):
        # Don't use cached/stale geocode, when constructing the LocationInfo below.
        # Force it to re-look-up from the fb location and cached geo lookups.
        db_event.location_geocode = None

    location_info = event_locations.LocationInfo(fb_dict, fb_event_attending_maybe=fb_event_attending_maybe, db_event=db_event)

    # Setup event's attendee-based location guess, in case we need it
    if fb_event_attending_maybe:
        ids = event_attendee_classifier._get_event_attendee_ids(fb_event_attending_maybe)
        start = time.time()
        top_geoname_id = person_city.get_top_geoname_for(ids)
        timelog.log_time_since('Guessing Location for Attendee IDs', start)
        db_event.attendee_geoname_id = top_geoname_id

        if top_geoname_id:
            # Undo the attempts to set the address earlier, that's not actually the right place to stick this (it overrides the fbevent location)
            top_city = cities_db.lookup_city_from_geoname_ids([top_geoname_id])[0]
            if db_event.address == top_city:
                db_event.address = ''

            logging.info('Guessing top city from attendees: %s', top_city.display_name())

    _update_geodata(db_event, location_info, disable_updates)


def clean_address(address):
    address = re.sub(r'B?\d*F?\d*$', '', address)
    return address


def _inner_make_event_findable_for_web_event(db_event, web_event, disable_updates):
    logging.info("Making web_event %s findable." % db_event.id)
    db_event.web_event = web_event

    db_event.fb_event = None
    db_event.owner_fb_uid = None

    db_event.attendee_count = 0  # Maybe someday set attending counts when we fetch them?

    if web_event['start_time'].endswith('Z'):
        web_event['start_time'] = web_event['start_time'][:-1]
    if web_event['end_time'] and web_event['end_time'].endswith('Z'):
        web_event['end_time'] = web_event['start_time'][:-1]

    db_event.start_time = dateutil.parser.parse(web_event['start_time']).replace(tzinfo=None)

    if web_event.get('end_time'):
        db_event.end_time = dateutil.parser.parse(web_event['end_time']).replace(tzinfo=None)
    else:
        db_event.end_time = None
    db_event.search_time_period = _event_time_period(db_event)

    db_event.event_keywords = event_classifier.relevant_keywords(db_event)
    db_event.auto_categories = [x.index_name for x in categories.find_styles(db_event) + categories.find_event_types(db_event)]

    geocode = None
    if web_event.get('location_address'):
        address = clean_address(web_event.get('location_address'))
        logging.info("Have location address, checking if it is geocodable: %s", web_event.get('location_address'))
        logging.info("Stripping off any floor info, final address is: %s", address)
        geocode = gmaps_api.lookup_address(address)
        if geocode is None:
            logging.warning("Received a location_address that was not geocodeable, treating as empty: %s", web_event['location_address'])
    if geocode is None:
        if web_event.get('latitude') or web_event.get('longitude'):
            logging.info("Have latlong, let's geocode that way: %s, %s", web_event.get('latitude'), web_event.get('longitude'))
            geocode = gmaps_api.lookup_latlng((web_event.get('latitude'), web_event.get('longitude')))
    if geocode is None:
        if web_event.get('geolocate_location_name'):
            logging.info("Have magic geolocate_location_name, checking if it is a place: %s", web_event.get('geolocate_location_name'))
            geocode = gmaps_api.lookup_location(web_event['geolocate_location_name'])
    if geocode is None:
        if web_event.get('location_name'):
            logging.info("Have regular location_name, checking if it is a place: %s", web_event.get('location_name'))
            geocode = gmaps_api.lookup_location(web_event['location_name'])
    if geocode:
        if 'name' in geocode.json_data:
            web_event['location_name'] = geocode.json_data['name']
        web_event['location_address'] = geocode.json_data['formatted_address']
        logging.info("Found an address: %s", web_event['location_address'])

        # We have a formatted_address, but that's it. Let's get a fully componentized address
        geocode_with_address = gmaps_api.lookup_address(clean_address(web_event['location_address']))
        if not geocode_with_address:
            logging.error("Could not get geocode for: %s", web_event['location_address'])
        elif 'address_components' not in geocode_with_address.json_data:
            logging.error("Could not get fully parsed address for: %s: %s", web_event['location_address'], geocode_with_address)
            pass
        elif 'country' not in web_event:
            web_event['country'] = geocode_with_address.country()
        elif web_event['country'] != geocode_with_address.country():
            logging.error(
                "Found incorrect address for venue! Expected %s but found %s", web_event['country'], geocode_with_address.country()
            )

        latlng = geocode.json_data['geometry']['location']
        web_event['latitude'] = latlng['lat']
        web_event['longitude'] = latlng['lng']

        # Add timezones, and save them to the web_event strings, for use by eventdata accessors
        timezone_string = timezone_finder.closest_timezone_at(lat=latlng['lat'], lng=latlng['lng'])
        web_event['timezone'] = timezone_string
        if timezone_string:
            tz = pytz.timezone(timezone_string)
            web_event['start_time'] = tz.localize(db_event.start_time).strftime(DATETIME_FORMAT_TZ)
            if db_event.end_time:
                web_event['end_time'] = tz.localize(db_event.end_time).strftime(DATETIME_FORMAT_TZ)
        else:
            logging.error('No timezone string found for latlng: %s', latlng)
    db_event.address = web_event.get('location_address')

    _inner_common_setup(db_event, disable_updates=disable_updates)

    if 'geodata' not in (disable_updates or []):
        # Don't use cached/stale geocode, when constructing the LocationInfo below.
        # Force it to re-look-up from the web data.
        if 'regeocode' not in (disable_updates or []):
            db_event.location_geocode = None
        location_info = event_locations.LocationInfo(db_event=db_event)
        _update_geodata(db_event, location_info, disable_updates)


def _inner_common_setup(db_event, disable_updates=None):
    if db_event.json_props is None:
        db_event.json_props = {}

    if 'photo' not in (disable_updates or []):
        _inner_cache_photo(db_event)

    text = '%s. %s' % (db_event.name, db_event.description)
    db_event.json_props['language'] = language.detect(text)


def _update_geodata(db_event, location_info, disable_updates):
    # Empty this out, we no longer care/need it
    db_event.nearby_city_names = []

    # If we got good values from before, don't overwrite with empty values!
    if not db_event.actual_city_name:
        logging.info('NO EVENT LOCATION1: %s', db_event.id)
        logging.info('NO EVENT LOCATION2: %s', location_info)
        logging.info('NO EVENT LOCATION3: %s', location_info.geocode)

    db_event.country = location_info.geocode.country() if location_info.geocode else None

    if location_info.geocode:
        geoname_city = cities_db.get_nearby_city(location_info.geocode.latlng(), country=location_info.geocode.country())
        if geoname_city:
            db_event.nearby_geoname_id = geoname_city.geoname_id
            db_event.city_name = geoname_city.display_name()
        else:
            db_event.nearby_geoname_id = None
            db_event.city_name = 'Unknown'
    else:
        db_event.city_name = "Unknown"
        db_event.nearby_geoname_id = None
    logging.info('Event %s decided on city %s', db_event.id, db_event.city_name)

    db_event.anywhere = location_info.is_online_event()
    db_event.actual_city_name = location_info.actual_city()
    if location_info.latlong():
        db_event.latitude, db_event.longitude = location_info.latlong()
    else:
        db_event.latitude = None
        db_event.longitude = None
        # TODO(lambert): find a better way of reporting/notifying about un-geocodeable addresses
        logging.warning("No geocoding results for eid=%s is: %s", db_event.id, location_info)

    # This only grabs the very first result from the raw underlying geocode request, since that's all that's used to construct the Geocode object in memory
    db_event.location_geocode = gmaps_api.convert_geocode_to_json(location_info.geocode)
