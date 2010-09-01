import datetime
import logging
import cPickle as pickle

from google.appengine.api import datastore
from google.appengine.ext import db

from events import cities
from events import tags

import locations

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
    final_url = square_url.replace('/q', '/%s' % event_image_type)
    return final_url


states_abbrev2full = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NA': 'National',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}

states_full2abbrev = {}
for abbr, full in states_abbrev2full.iteritems():
  states_full2abbrev[full] = abbr

def get_geocoded_location_for_event(fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {})
    address_components = [event_info.get('location'), venue.get('street'), venue.get('city'), states_full2abbrev.get(venue.get('state'), venue.get('state')), venue.get('country')]
    address_components = [x for x in address_components if x]
    address = ', '.join(address_components)
    logging.info("For event = %s, address is %s", fb_event['info']['id'], address)
    # Do not trust facebook for latitude/longitude data. It appears to treat LA as Louisiana, etc. So always geocode below.
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
    
    # searchable properties
    search_tags = db.StringListProperty()
    search_time_period = db.StringProperty()
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()
    search_regions = db.StringListProperty()

    # extra cached properties
    address = db.StringProperty()
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()

    def make_findable_for(self, fb_dict):
        # set up any cached fields or bucketing or whatnot for this event

        if fb_dict['deleted']:
            self.start_time = None
            self.end_time = None
            self.search_tags = []
            self.search_time_period = None
            self.search_regions = []
            return

        self.start_time = datetime.datetime.strptime(fb_dict['info']['start_time'], '%Y-%m-%dT%H:%M:%S+0000')
        self.end_time = datetime.datetime.strptime(fb_dict['info']['end_time'], '%Y-%m-%dT%H:%M:%S+0000')

        self.search_tags = [] # CHOREO and/or FREESTYLE
        if set(self.tags).intersection([x[0] for x in tags.FREESTYLE_EVENT_LIST]):
            self.search_tags.append(tags.FREESTYLE_EVENT)
        if set(self.tags).intersection([x[0] for x in tags.CHOREO_EVENT_LIST]):
            self.search_tags.append(tags.CHOREO_EVENT)

        self.search_time_period = None # PAST or FUTURE
        today = datetime.datetime.today()
        if today < self.end_time:
            self.search_time_period = tags.TIME_FUTURE
        else:
            self.search_time_period = tags.TIME_PAST

        results = get_geocoded_location_for_event(fb_dict)
        self.address = results['address']
        if results['latlng']:
            self.latitude = results['latlng'][0]
            self.longitude = results['latlng'][1]
            #TODO(lambert): Add enough cities to cities.py to support coverage over the entire US?
            # Or add a "default US" that always gets searched, and that gets appended if no cities are close enough.
            self.search_regions = cities.get_cities_within(self.latitude, self.longitude, REGION_RADIUS)
            logging.info("Nearest cities for %s are %s", self.address, self.search_regions)
            if not self.search_regions:
                logging.error("Error no search regions for eid=%s with lat/lng (%s,%s) with address %s", self.fb_event_id, self.latitude, self.longitude, self.address)
        else:
            #TODO(lambert): find a better way of reporting/notifying about un-geocodeable addresses
            logging.error("No geocoding results for eid=%s is: %s", self.fb_event_id, results)

    #def __repr__(self):
    #    return 'DBEvent(fb_event_id=%r,tags=%r)' % (self.fb_event_id, self.tags)
