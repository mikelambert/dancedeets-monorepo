from google.appengine.ext import db
from google.appengine.api import memcache
import gmaps

#memcache of: location str -> geocode lat long, address
#memcache of: fb_event_id -> event info
#db of: fbid, our_info

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


def memcache_event_key(fb_event_id):
    return 'Event.%s' % fb_event_id

def get_facebook_event_info(fb_event_id, facebook):
    memcache_key = memcache_event_key(fb_event_id)
    event_info = memcache.get(memcache_key)
    if not event_info:
        columns = 'eid,name,pic_small,pic_small,pic,description,start_time,end_time,creator,update_time,location,venue,privacy,hide_guest_list'
        query = 'select %s from event where eid = %s' % (columns, fb_event_id)
        event_infos = facebook.fql.query(query)
        event_info = event_infos[0]
        # TODO(lambert): do this with exceptions
        assert event_info['privacy'] == 'OPEN'
        assert event_info['hide_guest_list'] == False
        memcache.set(memcache_key, event_info, 10)
    return event_info

def memcache_event_friends_key(user_id, event_id):
    return 'Event.%s.%s' % (user_id, event_id)

def get_event_friends(facebook, event_id):
    memcache_key = memcache_event_friends_key(facebook.uid, event_id)
    event_friends = memcache.get(memcache_key)
    if not event_friends:
        event_friends = get_event_friends_from_facebook(facebook, event_id)
        memcache.set(memcache_key, event_friends, 10)
    return event_friends

def get_event_friends_from_facebook(facebook, event_id):
    def query_for(status):
        return 'select uid,name,pic_square,pic_big,pic_small from user where uid in (select uid2 from friend where uid1 = %s) and uid in (select uid from event_member where eid = %s and rsvp_status = "%s" )' % (facebook.uid, event_id, status)
    queries = dict((status, query_for(status)) for status in ('attending', 'unsure', 'declined', 'not_replied'))

    fql_results = facebook.fql.multiquery(queries)
    formatted_results = dict((x['name'], x['fql_result_set']) for x in fql_results)
    return formatted_results

def memcache_location_key(location):
    return 'Location.%s' % location

def get_geocoded_location(location):
    memcache_key = memcache_location_key(location)    
    geocoded_location = memcache.get(memcache_key)
    if not geocoded_location:
        geocoded_location = gmaps.get_geocoded_address(location)
        memcache.set(memcache_key, geocoded_location, 10)
    return geocoded_location

def get_db_event(fb_event_id):
    query = DBEvent.gql('where fb_event_id = :fb_event_id', fb_event_id=fb_event_id)
    results = query.fetch(1)
    if results:
        return results[0]
    else:
        return None


def get_geocoded_location_for_event(event_info):
    venue = event_info['venue']
    address_components = [event_info['location'], venue['street'], venue['city'], venue['state'], venue['country']]
    address_components = [x for x in address_components if x]
    address = ', '.join(address_components)
    results = {}
    if venue.get('latitude') and venue.get('longitude'):
        results['address'] = address
        results['lat'] = venue['latitude']
        results['lng'] = venue['longitude']
    else:
        geocoded = get_geocoded_location(address)
        results['address'] = geocoded['address']
        results['lat'] = geocoded['lat']
        results['lng'] = geocoded['lng']
    return results

# Wait to implement this until we know the API we want.
#def save_facebook_event(fb_event_id, db_event):
#    db_event = get_db_event(fb_event_id)
#    db_event.tags = tags
#    db_event.put()


class DBEvent(db.Model):
    """Stores custom data about our Event"""
    fb_event_id = db.IntegerProperty()
    # real data
    tags = db.StringListProperty()

    # cache of facebook data for querying purposes
    # or are we going to use googlebase for this?

    #def __repr__(self):
    #    return 'DBEvent(fb_event_id=%r,tags=%r)' % (self.fb_event_id, self.tags)

class FacebookEvent(object):
    def __init__(self, facebook, fb_event_id):
        self._facebook = facebook
        self._fb_event_id = fb_event_id
        self._db_event = None
        self._fb_event_info = None
        self._location = None
        self._fb_event_friends = None

    def _get_db_event(self):
        if not self._db_event:
            self._db_event = get_db_event(self._fb_event_id) or DBEvent(fb_event_id=self._fb_event_id)
            #self._db_event.title = 
        return self._db_event

    def _get_fb_event_info(self):
        if not self._fb_event_info:
            self._fb_event_info = get_facebook_event_info(self._fb_event_id, self._facebook)
        return self._fb_event_info
    get_fb_event_info = _get_fb_event_info

    def _get_location(self):
        if not self._location:
            self._location = get_geocoded_location_for_event(self._get_fb_event_info())
        return self._location
    get_location = _get_location

    def _get_fb_event_friends(self):
        if not self._fb_event_friends:
            self._fb_event_friends = get_event_friends(self._facebook, self._fb_event_id)
        return self._fb_event_friends
    get_fb_event_friends = _get_fb_event_friends

    def tags(self):
        return self._get_db_event().tags

    def set_tags(self, tags):
        event = self._get_db_event()
        event.tags = tags

    def save_db_event(self):
        event = self._get_db_event()
        event.put()

