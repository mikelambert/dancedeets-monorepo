import logging

from google.appengine.ext import ndb

import event_types
from loc import gmaps_api
from util import urls
from . import namespaces

REGION_RADIUS = 200 # kilometers


# valid parameters for creating_method= argument below
CM_AUTO = 'CM_AUTO'
CM_ADMIN = 'CM_ADMIN'
CM_USER = 'CM_USER'
CM_WEB_SCRAPE = 'CM_WEB_SCRAPE'


class DBEvent(ndb.Model):
    """Stores custom data about our Event"""

    @classmethod
    def generate_id(cls, namespace, namespaced_id):
        if namespace == namespaces.FACEBOOK:
            return namespaced_id
        else:
            return '%s:%s' % (namespace, namespaced_id)

    @property
    def id(self):
        return str(self.key.string_id())

    def __get_namespace_and_id(self):
        real_id = self.id
        if ':' in real_id:
            namespace, namespaced_id = real_id.split(':')
        else:
            namespace = namespaces.FACEBOOK
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
        return self.namespace == namespaces.FACEBOOK

    @property
    def fb_event_id(self):
        if self.is_facebook_event:
            return self.namespaced_id
        else:
            raise ValueError("Not an FB Event: %s" % self.id)

    # Fields unique to Facebook:
    owner_fb_uid = ndb.StringProperty()
    visible_to_fb_uids = ndb.StringProperty(indexed=False, repeated=True)
    # derived data from fb_event itself
    fb_event = ndb.JsonProperty(indexed=False)

    #STR_ID_MIGRATE (Old, to be migrated...to namespaced_creator)
    creating_fb_uid = ndb.IntegerProperty()
    # # TODO: WEB_EVENTS: IMPLEMENT AND MIGRATE DATA
    # namespaced_creator = ndb.StringProperty()

    # The blob of data that we received from the scraper
    web_event = ndb.JsonProperty(indexed=False)

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

    def has_content(self):
        if self.web_event:
            return True
        else:
            return not self.fb_event['empty']

    @property
    def start_time_string(self):
        if self.web_event:
            return self.web_event['start_time']
        else:
            return self.fb_event['info']['start_time']

    @property
    def end_time_string(self):
        if self.web_event:
            return self.web_event['end_time']
        else:
            return self.fb_event['info'].get('end_time')

    @property
    def source_url(self):
        return namespaces.NAMESPACES[self.namespace].event_url_func(self)

    @property
    def source_name(self):
        return namespaces.NAMESPACES[self.namespace].long_name

    @property
    def empty_reason(self):
        return self.fb_event['empty']

    @property
    def name(self):
        if self.web_event:
            return self.web_event['name']
        else:
            return self.fb_event['info'].get('name', '')

    @property
    def description(self):
        if self.web_event:
            return self.web_event['description']
        else:
            return self.fb_event['info'].get('description', '')

    @property
    def categories(self):
        return event_types.humanize_categories(self.auto_categories)

    @property
    def cover_metadata(self):
        return self.fb_event['info'].get('cover')

    @property
    def cover_images(self):
        if self.web_event:
            return [{
                'source': self.image_url,
                'height': 0,  # TODO: WEB_EVENTS find these fields
                'width': 0,
            }]
        else:
            if 'cover_info' in self.fb_event:
                # Old FB API versions returned ints instead of strings, so let's stringify manually to ensure we can look up the cover_info
                cover = self.fb_event['cover_info'][str(self.fb_event['info']['cover']['cover_id'])]
                return cover['images']
            else:
                return []

    @property
    def largest_cover(self):
        cover_images = self.cover_images
        if cover_images:
            return max(cover_images, key=lambda x: x['height'])
        else:
            return None

    @property
    def image_url(self):
        if self.web_event:
            return self.web_event['photo']
        else:
            # old school data
            picture_url = self.fb_event.get('fql_info') or self.fb_event.get('picture_urls')
            # TODO(FB2.0): cleanup!
            if self.fb_event.get('picture'):
                if isinstance(self.fb_event['picture'], basestring):
                    return self.fb_event['picture']
                else:
                    return self.fb_event['picture']['data']['url']
            elif picture_url and picture_url['data']:
                return picture_url['data'][0]['pic_big']
            else:
                logging.error("Error loading picture for event id %s", self.fb_event['info']['id'])
                return urls.fb_event_image_url(self.fb_event['info']['id'])

    @property
    def location_name(self):
        if self.web_event:
            return self.web_event.get('location_name')
        else:
            return self.fb_event['info'].get('location', '')

    @property
    def venue(self):
        if self.web_event:
            # TODO: WEB_EVENTS
            return None
        else:
            return self.fb_event['info'].get('venue', {})

    @property
    def full_address(self):
        if self.web_event:
            return self.web_event.get('location_address')
        else:
            if self.street_address:
                return '%s\n%s' % (self.street_address, self.city_state_country)
            else:
                return self.city_state_country

    @property
    def street_address(self):
        # TODO: WEB_EVENTS (why doesn't our location show up in the event page?)
        return self.venue.get('street')

    @property
    def city(self):
        return self.venue.get('city')

    @property
    def state(self):
        return self.venue.get('state')

    @property
    def city_state_country(self):
        city_state_country = [x for x in [self.city, self.state, self.country] if x]
        return ', '.join(city_state_country)

    # @property
    # def country(self):
    #     return self.venue.get('country')
    #
    # @property
    # def latitude(self):
    #     return self.venue and self.venue.get('latitude')
    #
    # @property
    # def longitude(self):
    #     return self.venue and self.venue.get('longitude')

    @property
    def attending_count(self):
        return self.attendee_count

    @property
    def maybe_count(self):
        if self.web_event:
            return 0
        else:
            return self.fb_event['info'].get('maybe_count')

    @property
    def admins(self):
        if self.web_event:
            return []
        else:
            admins = self.fb_event['info'].get('admins', {}).get('data')
            if not admins:
                if self.fb_event['info'].get('owner'):
                    admins = [self.fb_event['info'].get('owner')]
                else:
                    admins = []
            return admins
