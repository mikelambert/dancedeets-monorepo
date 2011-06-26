import datetime
import logging
import cPickle as pickle
import time

from google.appengine.api import datastore
from google.appengine.runtime import apiproxy_errors
from google.appengine.ext import db

from events import cities
from events import tags
import geohash

import locations
from util import abbrev
from util import dates

import smemcache

REGION_RADIUS = 200 # kilometers
CHOOSE_RSVPS = ['attending', 'maybe', 'declined']

ONLINE_ADDRESS = 'ONLINE'

# pic url prefixes:
# increasing-size: t, s, n
# square: q

EVENT_IMAGE_SMALL = 't'
EVENT_IMAGE_MEDIUM = 's'
EVENT_IMAGE_LARGE = 'n'
EVENT_IMAGE_SQUARE = 'q'
EVENT_IMAGE_TYPES = [EVENT_IMAGE_SMALL, EVENT_IMAGE_MEDIUM, EVENT_IMAGE_LARGE, EVENT_IMAGE_SQUARE]


def get_event_image_url(square_url, event_image_type):
    assert event_image_type in EVENT_IMAGE_TYPES
    url = square_url
    url = url.replace('/q', '/%s' % event_image_type)
    url = url.replace('_q', '_%s' % event_image_type)
    return url

class LocationMapping(db.Model):
    remapped_address = db.StringProperty()

def get_original_address_for_event(fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {})
    # Use states_full2abbrev to convert "Lousiana" to "LA" so "Hollywood, LA" geocodes correctly.
    state = abbrev.states_full2abbrev.get(venue.get('state'), venue.get('state'))
    if venue.get('city') and (state or venue.get('country')):
        address_components = [venue.get('city'), state, venue.get('country')]
    else:
        address_components = [event_info.get('location'), venue.get('street'), venue.get('city'), state, venue.get('country')]
    address_components = [x for x in address_components if x]
    address = ', '.join(address_components)
    return address

def get_remapped_address_for(address):
    if not address:
        return ''
    # map locations to corrected locations for events that have wrong or incomplete info
    location_mapping = LocationMapping.get_by_key_name(address)
    if location_mapping:
        address = location_mapping.remapped_address
        return address
    else:
        return None

def save_remapped_address_for(original_address, new_remapped_address):
    if original_address:
        location_mapping = LocationMapping.get_or_insert(original_address)
        location_mapping.remapped_address = new_remapped_address
        try:
            location_mapping.put()
        except apiproxy_errors.CapabilityDisabledError:
            pass

#TODO(lambert): make db_event an optional param at the end of the param list
def get_usable_address_for_event(db_event, fb_event):
    # Do not trust facebook for latitude/longitude data. It appears to treat LA as Louisiana, etc. So always geocode
    address = get_original_address_for_event(fb_event)
    logging.info("For event = %s, address is %s", fb_event['info']['id'], address)

    if db_event and db_event.address:
        logging.info("address overridden to %s", db_event.address)
        address = db_event.address
    elif address:
        remapped_address = get_remapped_address_for(address)
        if remapped_address:
            logging.info("address remapped to %s", remapped_address)
            address = remapped_address
    return address

def get_geocoded_location_for_event(db_event, fb_event):
    address = get_usable_address_for_event(db_event, fb_event)
    results = locations.get_geocoded_location(address)
    return results

def parse_fb_timestamp(fb_timestamp):
    # because of events like 23705144628 without any time information
    if not fb_timestamp:
        return datetime.datetime(1970, 1, 1)

    # If we access events with an access_token (necessary to get around DOS limits from overloaded appengine IPs), we get a timestamp-localized weirdly-timed time from facebook, and need to reverse-engineer it
    if '+' in fb_timestamp:
        return dates.localize_timestamp(datetime.datetime.strptime(fb_timestamp.split('+')[0], '%Y-%m-%dT%H:%M:%S'))
    else:
        return datetime.datetime.strptime(fb_timestamp, '%Y-%m-%dT%H:%M:%S')


DBEVENT_PREFIX = 'DbEvent.%s'
def get_cached_db_events(event_ids, allow_cache=True):
    db_events = []
    a = time.time()
    if allow_cache:
        memcache_keys = [DBEVENT_PREFIX % x for x in event_ids]
        db_events = smemcache.get_multi(memcache_keys).values()
        logging.info("loading db events from memcache (included below) took %s seconds", time.time() - a)
    remaining_event_ids = set(event_ids).difference([x.fb_event_id for x in db_events])
    if remaining_event_ids:
        new_db_events = DBEvent.get_by_key_name([str(x) for x in remaining_event_ids])
        smemcache.safe_set_memcache(dict((DBEVENT_PREFIX % x.fb_event_id, x) for x in new_db_events), expiry=2*3600)
        db_events += new_db_events
    db_event_map = dict((x.fb_event_id, x) for x in db_events)
    logging.info("loading cached db events took %s seconds", time.time() - a)
    return [db_event_map[x] for x in event_ids]


class DBEvent(db.Model):
    """Stores custom data about our Event"""
    fb_event_id = property(lambda x: int(x.key().name()))

    # real data
    tags = db.StringListProperty()
    owner_fb_uid = db.StringProperty()
    creating_fb_uid = db.IntegerProperty()
    creation_time = db.DateTimeProperty()
    
    # searchable properties
    search_tags = db.StringListProperty()
    search_time_period = db.StringProperty()
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()
    attendee_count = db.IntegerProperty()

    # extra cached properties
    address = db.StringProperty()
    actual_city_name = db.StringProperty() # city for this event
    city_name = db.StringProperty() # largest nearby city for this event
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    geohashes = db.StringListProperty()
    anywhere = db.BooleanProperty()

    search_regions = db.StringListProperty()

    def include_attending_summary(self, fb_dict):
        attendees = fb_dict['attending']['data']
        self.attendee_count = len(attendees)

    def make_findable_for(self, fb_dict):
        # set up any cached fields or bucketing or whatnot for this event

        if fb_dict['deleted']:
            self.start_time = None
            self.end_time = None
            self.search_tags = []
            self.search_time_period = None
            self.address = None
            self.actual_city_name = None
            self.city_name = None
            return

        if 'owner' in fb_dict['info']:
            self.owner_fb_uid = fb_dict['info']['owner']['id']
        else:
            self.owner_fb_uid = None

        self.start_time = parse_fb_timestamp(fb_dict['info'].get('start_time'))
        self.end_time = parse_fb_timestamp(fb_dict['info'].get('end_time'))

        self.search_tags = [] # CHOREO and/or FREESTYLE
        if set(self.tags).intersection([x[0] for x in tags.FREESTYLE_EVENT_LIST]):
            self.search_tags.append(tags.FREESTYLE_EVENT)
        if set(self.tags).intersection([x[0] for x in tags.CHOREO_EVENT_LIST]):
            self.search_tags.append(tags.CHOREO_EVENT)

        self.search_time_period = None # PAST or FUTURE
        today = datetime.datetime.today() - datetime.timedelta(days=1)
        if today < self.end_time:
            self.search_time_period = tags.TIME_FUTURE
        else:
            self.search_time_period = tags.TIME_PAST

        address = get_usable_address_for_event(self, fb_dict)
        logging.info("%r %r", address, ONLINE_ADDRESS)
        self.anywhere = (address == ONLINE_ADDRESS)

        results = locations.get_geocoded_location(address)
        self.actual_city_name = results['city']
        self.city_name = cities.get_largest_nearby_city_name(self.address or results['address'])

        if results['latlng'][0] is not None:
            self.latitude = results['latlng'][0]
            self.longitude = results['latlng'][1]
            self.geohashes = []
            for x in range(locations.max_geohash_bits):
                self.geohashes.append(str(geohash.Geostring((self.latitude, self.longitude), depth=x)))
        else:
            self.latitude = None
            self.longitude = None
            self.geohashes = []
            #TODO(lambert): find a better way of reporting/notifying about un-geocodeable addresses
            logging.warning("No geocoding results for eid=%s is: %s", self.fb_event_id, results)

    #def __repr__(self):
    #    return 'DBEvent(fb_event_id=%r,tags=%r)' % (self.fb_event_id, self.tags)
