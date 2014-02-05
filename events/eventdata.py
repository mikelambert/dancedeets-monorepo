import datetime
import logging
import time

from google.appengine.ext import db

from util import dates
from util import urls

import smemcache

REGION_RADIUS = 200 # kilometers
CHOOSE_RSVPS = ['attending', 'maybe', 'declined']

TIME_PAST = 'PAST'
TIME_FUTURE = 'FUTURE'


def event_time_period(start_time, end_time):
    event_end_time = dates.faked_end_time(start_time, end_time)
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    event_relative = (event_end_time - today).total_seconds()
    if event_relative > 0:
        return TIME_FUTURE
    else:
        return TIME_PAST

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

    #def __repr__(self):
    #    return 'DBEvent(fb_event_id=%r,tags=%r)' % (self.fb_event_id, self.tags)
