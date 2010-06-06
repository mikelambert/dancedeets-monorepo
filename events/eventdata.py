import cPickle as pickle
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


class DBEvent(db.Model):
    """Stores custom data about our Event"""
    fb_event_id = db.IntegerProperty()
    # real data
    tags = db.StringListProperty()

    def make_findable_for(self, fb_dict):
        # set up any cached fields or bucketing or whatnot for this event
        pass

    #def __repr__(self):
    #    return 'DBEvent(fb_event_id=%r,tags=%r)' % (self.fb_event_id, self.tags)
