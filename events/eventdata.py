import datetime
import logging
import cPickle as pickle

from google.appengine.api import datastore
from google.appengine.runtime import apiproxy_errors
from google.appengine.ext import db

from events import cities
from events import tags
import geohash

import locations
from util import abbrev
from util import dates

REGION_RADIUS = 200 # kilometers
CHOOSE_RSVPS = ['attending', 'maybe', 'declined']

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
    # Use staes_full2abbrev to convert "Lousiana" to "LA" so "Hollywood, LA" geocodes correctly.
    address_components = [event_info.get('location'), venue.get('street'), venue.get('city'), abbrev.states_full2abbrev.get(venue.get('state'), venue.get('state')), venue.get('country')]
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

def get_geocoded_location_for_event(fb_event):
    # Do not trust facebook for latitude/longitude data. It appears to treat LA as Louisiana, etc. So always geocode
    address = get_original_address_for_event(fb_event)
    logging.info("For event = %s, address is %s", fb_event['info']['id'], address)

    if address:
        remapped_address = get_remapped_address_for(address)
        if remapped_address:
            logging.info("address got remapped to %s", remapped_address)
            address = remapped_address

    results = locations.get_geocoded_location(address)
    return results

def parse_fb_timestamp(fb_timestamp):
    return dates.localize_timestamp(datetime.datetime.strptime(fb_timestamp, '%Y-%m-%dT%H:%M:%S+0000'))

class DBEvent(db.Model):
    """Stores custom data about our Event"""
    fb_event_id = property(lambda x: int(x.key().name()))

    # real data
    tags = db.StringListProperty()
    creating_fb_uid = db.IntegerProperty()
    creation_time = db.DateTimeProperty()
    
    # searchable properties
    search_tags = db.StringListProperty()
    search_time_period = db.StringProperty()
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()

    # extra cached properties
    address = db.StringProperty()
    city_name = db.StringProperty()
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    geohashes = db.StringListProperty()

    search_regions = db.StringListProperty()

    def make_findable_for(self, fb_dict):
        # set up any cached fields or bucketing or whatnot for this event

        if fb_dict['deleted']:
            self.start_time = None
            self.end_time = None
            self.search_tags = []
            self.search_time_period = None
            self.address = None
            self.city_name = None
            return

        self.start_time = dates.localize_timestamp(datetime.datetime.strptime(fb_dict['info']['start_time'], '%Y-%m-%dT%H:%M:%S+0000'))
        self.end_time = dates.localize_timestamp(datetime.datetime.strptime(fb_dict['info']['end_time'], '%Y-%m-%dT%H:%M:%S+0000'))

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

        results = get_geocoded_location_for_event(fb_dict)
        self.address = results['address']
        self.city_name = cities.get_largest_nearby_city_name(self.address)

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
            logging.error("No geocoding results for eid=%s is: %s", self.fb_event_id, results)

    #def __repr__(self):
    #    return 'DBEvent(fb_event_id=%r,tags=%r)' % (self.fb_event_id, self.tags)
