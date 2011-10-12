import datetime
import logging
import cPickle as pickle
import time

from google.appengine.runtime import apiproxy_errors
from google.appengine.ext import db

from events import cities
import geohash

import locations
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

TIME_PAST = 'PAST'
TIME_FUTURE = 'FUTURE'

def get_event_image_url(square_url, event_image_type):
    assert event_image_type in EVENT_IMAGE_TYPES
    url = square_url
    url = url.replace('/q', '/%s' % event_image_type)
    url = url.replace('_q', '_%s' % event_image_type)
    return url


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

    # TODO(lambert): right now this is unused, but maybe we want to cache our "ish" tags or something to that effect?
    tags = db.StringListProperty()

    # real data
    owner_fb_uid = db.StringProperty()
    creating_fb_uid = db.IntegerProperty()
    creation_time = db.DateTimeProperty()
    # could be AUTO, ADMIN, USER, etc? Helps for maintaining a proper training corpus
    #TODO(lambert): start using this field in auto-created events
    creating_method = db.StringProperty()

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

        self.start_time = dates.parse_fb_timestamp(fb_dict['info'].get('start_time'))
        self.end_time = dates.parse_fb_timestamp(fb_dict['info'].get('end_time'))

        self.search_time_period = None # PAST or FUTURE
        today = datetime.datetime.today() - datetime.timedelta(days=1)
        if today < self.end_time:
            self.search_time_period = TIME_FUTURE
        else:
            self.search_time_period = TIME_PAST

        #TODO(lambert): inline when we solve 'anywhere' problem
        address = event_locations.get_usable_address_for_event(self, fb_dict)
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
