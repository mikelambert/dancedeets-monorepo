import datetime
import logging
import cPickle as pickle
import time

from google.appengine.runtime import apiproxy_errors
from google.appengine.ext import db

from events import cities
import geohash
import locations
from logic import event_classifier
from logic import event_locations
from util import dates
from util import urls

import smemcache

REGION_RADIUS = 200 # kilometers
CHOOSE_RSVPS = ['attending', 'maybe', 'declined']

TIME_PAST = 'PAST'
TIME_FUTURE = 'FUTURE'

def get_event_image_url(fb_event):
    picture_url = fb_event.get('fql_info') or fb_event.get('picture_urls')
    # TODO(lambert): delete else clause once we've loaded picture_urls for everything?
    if picture_url and picture_url['data']:
        return picture_url['data'][0]['pic_big']
    else:
        logging.error("Error loading picture for event id %s", fb_event['info']['id'])
        return urls.fb_event_image_url(fb_event['info']['id'])


DBEVENT_PREFIX = 'DbEvent.%s'
def cache_db_events(events):
    return smemcache.safe_set_memcache(dict((DBEVENT_PREFIX % x.fb_event_id, x) for x in events), expiry=2*3600)

def get_cached_db_events(event_ids, allow_cache=True):
    db_events = []
    a = time.time()
    if allow_cache:
        memcache_keys = [DBEVENT_PREFIX % x for x in event_ids]
        db_events = smemcache.get_multi(memcache_keys).values()
        logging.info("loading db events from memcache (included below) took %s seconds", time.time() - a)
    remaining_event_ids = set(event_ids).difference([x.fb_event_id for x in db_events if x])
    if remaining_event_ids:
        new_db_events = DBEvent.get_by_key_name([str(x) for x in remaining_event_ids])
        new_db_events = [x for x in new_db_events if x]
        cache_db_events(new_db_events)
        db_events += new_db_events
    db_event_map = dict((x.fb_event_id, x) for x in db_events)
    logging.info("loading cached db events took %s seconds", time.time() - a)
    return [db_event_map.get(x, None) for x in event_ids]

CM_AUTO = 'CM_AUTO'
CM_ADMIN = 'CM_ADMIN'
CM_USER = 'CM_USER'

class DBEvent(db.Model):
    """Stores custom data about our Event"""
    fb_event_id = property(lambda x: int(x.key().name()))

    # TODO(lambert): right now this is unused, but maybe we want to cache our "ish" tags or something to that effect?
    tags = db.StringListProperty(indexed=False)
    search_tags = db.StringListProperty(indexed=False) # old classification-system tags
    search_regions = db.StringListProperty(indexed=False) # not sure what this was ever used for

    # real data
    owner_fb_uid = db.StringProperty()
    creating_fb_uid = db.IntegerProperty(indexed=False)
    creation_time = db.DateTimeProperty(indexed=False)
    # could be AUTO, ADMIN, USER, etc? Helps for maintaining a proper training corpus
    #TODO(lambert): start using this field in auto-created events
    creating_method = db.StringProperty(indexed=False)

    # searchable properties
    search_time_period = db.StringProperty()
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()
    attendee_count = db.IntegerProperty()

    # extra cached properties
    address = db.StringProperty(indexed=False) # manually overridden address
    actual_city_name = db.StringProperty(indexed=False) # city for this event
    city_name = db.StringProperty() # largest nearby city for this event
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    geohashes = db.StringListProperty()
    anywhere = db.BooleanProperty()

    event_keywords = db.StringListProperty(indexed=False)


    def include_attending_summary(self, fb_dict):
        attendees = fb_dict['attending']['data']
        self.attendee_count = len(attendees)

    def make_findable_for(self, batch_lookup, fb_dict):
        # set up any cached fields or bucketing or whatnot for this event

        if fb_dict['deleted']:
            self.start_time = None
            self.end_time = None
            self.search_time_period = None
            self.address = None
            self.actual_city_name = None
            self.city_name = None
            return

        if 'owner' in fb_dict['info']:
            self.owner_fb_uid = fb_dict['info']['owner']['id']
        else:
            self.owner_fb_uid = None

        self.start_time = dates.parse_fb_start_time(fb_dict)
        self.end_time = dates.parse_fb_end_time(fb_dict)

        self.search_time_period = None # PAST or FUTURE
        today = datetime.datetime.today() - datetime.timedelta(days=1)
        if today < self.end_time:
            self.search_time_period = TIME_FUTURE
        else:
            self.search_time_period = TIME_PAST

        location_info = event_locations.LocationInfo(batch_lookup, fb_dict, db_event=self)
        # If we got good values from before, don't overwrite with empty values!
        if location_info.actual_city() or not self.actual_city_name:
            self.anywhere = location_info.is_online_event()
            self.actual_city_name = location_info.actual_city()
            self.city_name = location_info.largest_nearby_city()
            if self.actual_city_name:
                self.latitude, self.longitude = location_info.latlong()
                self.geohashes = []
                for x in range(locations.max_geohash_bits):
                    self.geohashes.append(str(geohash.Geostring((self.latitude, self.longitude), depth=x)))
            else:
                self.latitude = None
                self.longitude = None
                self.geohashes = []
                #TODO(lambert): find a better way of reporting/notifying about un-geocodeable addresses
                logging.warning("No geocoding results for eid=%s is: %s", self.fb_event_id)

        self.event_keywords = event_classifier.relevant_keywords(fb_dict)

    #def __repr__(self):
    #    return 'DBEvent(fb_event_id=%r,tags=%r)' % (self.fb_event_id, self.tags)
