from google.appengine.ext import db
from google.appengine.api import memcache
import locations

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
        geocoded = locations.get_geocoded_location(address)
        results['address'] = geocoded['address']
        results['lat'] = geocoded['lat']
        results['lng'] = geocoded['lng']
    return results

def get_db_event(fb_event_id):
    query = DBEvent.gql('where fb_event_id = :fb_event_id', fb_event_id=fb_event_id)
    results = query.fetch(1)
    if results:
        return results[0]
    else:
        return None


class DBEvent(db.Model):
    """Stores custom data about our Event"""
    fb_event_id = db.IntegerProperty()
    # real data
    tags = db.StringListProperty()

    # cache of facebook data for querying purposes
    # or are we going to use googlebase for this?

    #def __repr__(self):
    #    return 'DBEvent(fb_event_id=%r,tags=%r)' % (self.fb_event_id, self.tags)
