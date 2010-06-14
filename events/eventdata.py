import datetime
import cPickle as pickle

from google.appengine.api import datastore
from google.appengine.ext import db

import locations

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
    final_url = square_url.replace('/q', '/%s' % event_image_type)
    return final_url


def get_geocoded_location_for_event(fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {})
    address_components = [event_info.get('location'), venue.get('street'), venue.get('city'), venue.get('state'), venue.get('country')]
    address_components = [x for x in address_components if x]
    address = ', '.join(address_components)
    results = {}
    if venue.get('latitude') and venue.get('longitude'):
        results['address'] = address
        results['latlng'] = (venue['latitude'], venue['longitude'])
    else:
        results = locations.get_geocoded_location(address)
    return results


def get_db_event(fb_event_id):
    query = DBEvent.gql('where fb_event_id = :fb_event_id', fb_event_id=fb_event_id)
    results = query.fetch(1)
    if results:
        return results[0]
    else:
        return None

def get_db_events(fb_event_ids):
    db_events = []
    max_in_queries = datastore.MAX_ALLOWABLE_QUERIES
    for i in range(0, len(fb_event_ids), max_in_queries):
        fb_event_ids_str = ','.join(str(x) for x in fb_event_ids[i:i+max_in_queries])
        db_events.extend(DBEvent.gql('where fb_event_id in (%s)' % fb_event_ids_str))
    return db_events

    

class DBEvent(db.Model):
    """Stores custom data about our Event"""
    fb_event_id = db.IntegerProperty()
    # real data
    tags = db.StringListProperty()
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()

    def make_findable_for(self, fb_dict):
        # set up any cached fields or bucketing or whatnot for this event

        self.start_time = datetime.datetime.strptime(fb_dict['info']['start_time'], '%Y-%m-%dT%H:%M:%S+0000')
        self.end_time = datetime.datetime.strptime(fb_dict['info']['end_time'], '%Y-%m-%dT%H:%M:%S+0000')

    #def __repr__(self):
    #    return 'DBEvent(fb_event_id=%r,tags=%r)' % (self.fb_event_id, self.tags)
