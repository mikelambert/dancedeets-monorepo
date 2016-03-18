import logging

from google.appengine.ext import ndb

from loc import gmaps_api
from util import urls

REGION_RADIUS = 200 # kilometers


def get_event_image_url(fb_event):
    # old school data
    picture_url = fb_event.get('fql_info') or fb_event.get('picture_urls')
    # TODO(FB2.0): cleanup!
    if fb_event.get('picture'):
        if isinstance(fb_event['picture'], basestring):
            return fb_event['picture']
        else:
            return fb_event['picture']['data']['url']
    elif picture_url and picture_url['data']:
        return picture_url['data'][0]['pic_big']
    else:
        logging.error("Error loading picture for event id %s", fb_event['info']['id'])
        return urls.fb_event_image_url(fb_event['info']['id'])


def get_largest_cover(fb_event):
    if 'cover_info' in fb_event:
        # Sometimes cover_id is an int or a string, but cover_info is always a string.
        cover = fb_event['cover_info'][str(fb_event['info']['cover']['cover_id'])]
        max_cover = max(cover['images'], key=lambda x: x['height'])
        return max_cover
    else:
        return None

# valid parameters for creating_method= argument below
CM_AUTO = 'CM_AUTO'
CM_ADMIN = 'CM_ADMIN'
CM_USER = 'CM_USER'

NAMESPACE_FACEBOOK = 'FB'


class DBEvent(ndb.Model):
    """Stores custom data about our Event"""

    def __get_namespace_and_id(self):
        real_id = str(self.key.string_id())
        if ':' in real_id:
            namespace, namespaced_id = real_id.split(':')
        else:
            namespace = NAMESPACE_FACEBOOK
            namespaced_id = real_id
        return namespace, namespaced_id

    @property
    def namespace(self):
        return self.__get_namespace_and_id()[0]

    @property
    def namespaced_id(self):
        return self.__get_namespace_and_id()[1]

    @property
    def is_facebook_event(self):
        return self.namespace == NAMESPACE_FACEBOOK

    @property
    def fb_event_id(self):
        if self.is_facebook_event:
            return self.namespaced_id
        else:
            raise ValueError("Not an FB Event: %s" % self.real_id)

    # Fields unique to Facebook:
    owner_fb_uid = ndb.StringProperty()
    visible_to_fb_uids = ndb.StringProperty(indexed=False, repeated=True)
    # derived data from fb_event itself
    fb_event = ndb.JsonProperty(indexed=False)

    #STR_ID_MIGRATE (Old, to be migrated...to namespaced_creator)
    creating_fb_uid = ndb.IntegerProperty()
    # TODO: IMPLEMENT AND MIGRATE
    # namespaced_creator = ndb.StringProperty()

    creation_time = ndb.DateTimeProperty(auto_now_add=True)
    # could be AUTO, ADMIN, USER, etc? Helps for maintaining a proper training corpus
    creating_method = ndb.StringProperty()

    # searchable properties
    search_time_period = ndb.StringProperty()
    start_time = ndb.DateTimeProperty(indexed=False)
    end_time = ndb.DateTimeProperty(indexed=False)
    attendee_count = ndb.IntegerProperty(indexed=False)

    # extra cached properties
    address = ndb.StringProperty(indexed=False) # manually overridden address
    actual_city_name = ndb.StringProperty(indexed=False) # city for this event
    # Index is needed for city_name=Unknown searches in admin_nolocation_events
    city_name = ndb.StringProperty() # largest nearby city for this event
    latitude = ndb.FloatProperty(indexed=False)
    longitude = ndb.FloatProperty(indexed=False)
    anywhere = ndb.BooleanProperty()

    location_geocode = ndb.JsonProperty(indexed=False)

    event_keywords = ndb.StringProperty(indexed=False, repeated=True)
    auto_categories = ndb.StringProperty(indexed=False, repeated=True)
    country = ndb.StringProperty(indexed=False)

    # TODO(lambert): right now this is unused, but maybe we want to cache our "ish" tags or something to that effect?
    # Was originally used to track manually-applied tags, and contains that data for some old events...
    tags = ndb.StringProperty(indexed=False, repeated=True)

    def get_geocode(self):
        return gmaps_api.parse_geocode(self.location_geocode)

    def has_geocode(self):
        return self.location_geocode is not None and self.location_geocode.get('status') == 'OK'

    @classmethod
    def get_by_ids(cls, id_list, keys_only=False):
        if not id_list:
            return []
        keys = [ndb.Key(cls, x) for x in id_list]
        if keys_only:
            return cls.query(cls.key.IN(keys)).fetch(len(keys), keys_only=True)
        else:
            return ndb.get_multi(keys)
