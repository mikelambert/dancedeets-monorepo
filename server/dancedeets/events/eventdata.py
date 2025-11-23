import datetime
import dateutil
import logging
import re
import pytz

from google.cloud import ndb

from dancedeets import event_types
from dancedeets.events import event_locations
from dancedeets.loc import address
from dancedeets.loc import gmaps_api
from . import namespaces
from dancedeets.util import fb_events

REGION_RADIUS = 200  # kilometers

# valid parameters for creating_method= argument below
CM_AUTO = 'CM_AUTO'  # A FBEvent we found via fb pages/groups and signed-in fb users
CM_AUTO_ATTENDEE = 'CM_AUTO_ATTENDEE'  # A FBEvent we found via event-attendees
CM_AUTO_WEB = 'CM_AUTO_WEB'  # A FBEvent we scraped from the web
CM_ADMIN = 'CM_ADMIN'
CM_USER = 'CM_USER'
CM_WEB_SCRAPE = 'CM_WEB_SCRAPE'  # A WebEvent we scraped from the web
CM_UNKNOWN = 'CM_UNKNOWN'

ALL_CM_HUMAN_CREATED = [CM_ADMIN, CM_USER]

EVENT_ID_REGEX = r'(?:\d+|[^/?#]+:[^/?#]+)'


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
    def is_fb_event(self):
        return self.namespace == namespaces.FACEBOOK

    @property
    def fb_event_id(self):
        if self.is_fb_event:
            return self.namespaced_id
        else:
            raise ValueError("Not an FB Event: %s" % self.id)

    # Use this for now to separate our shown-events vs non-shown-events
    verticals = ndb.StringProperty(repeated=True)

    # Fields unique to Facebook:
    owner_fb_uid = ndb.StringProperty()
    admin_fb_uids = ndb.StringProperty(repeated=True)
    visible_to_fb_uids = ndb.StringProperty(indexed=False, repeated=True)
    # derived data from fb_event itself
    fb_event = ndb.JsonProperty(indexed=False)

    json_props = ndb.JsonProperty(indexed=False)

    #STR_ID_MIGRATE (Old, to be migrated...to namespaced_creator)
    creating_fb_uid = ndb.IntegerProperty()
    creating_name = ndb.StringProperty()
    # # TODO: WEB_EVENTS: IMPLEMENT AND MIGRATE DATA
    # namespaced_creator = ndb.StringProperty()

    namespace_copy = ndb.StringProperty()

    # The blob of data that we received from the scraper
    web_event = ndb.JsonProperty(indexed=False)

    creation_time = ndb.DateTimeProperty(auto_now_add=True)
    # could be AUTO, ADMIN, USER, etc? Helps for maintaining a proper training corpus
    creating_method = ndb.StringProperty()

    # searchable properties
    search_time_period = ndb.StringProperty()
    start_time = ndb.DateTimeProperty(indexed=True)  # needed to composite index
    end_time = ndb.DateTimeProperty(indexed=False)
    attendee_count = ndb.IntegerProperty(indexed=False)

    # extra cached properties
    address = ndb.StringProperty(indexed=False)  # manually overridden address
    actual_city_name = ndb.StringProperty()  # city for this event
    # Index is needed for city_name=Unknown searches in admin_nolocation_events
    city_name = ndb.StringProperty()  # largest nearby city for this event
    nearby_geoname_id = ndb.IntegerProperty()  # largest nearby city (geoname id) for this event
    attendee_geoname_id = ndb.IntegerProperty()  # the best-guess location from the event attendees

    latitude = ndb.FloatProperty(indexed=True)  # needed to composite index
    longitude = ndb.FloatProperty(indexed=False)
    anywhere = ndb.BooleanProperty()

    location_geocode = ndb.JsonProperty(indexed=False)

    event_keywords = ndb.StringProperty(indexed=False, repeated=True)
    auto_categories = ndb.StringProperty(indexed=False, repeated=True)
    country = ndb.StringProperty(indexed=False)

    # TODO(lambert): right now this is unused, but maybe we want to cache our "ish" tags or something to that effect?
    # Was originally used to track manually-applied tags, and contains that data for some old events...
    tags = ndb.StringProperty(indexed=False, repeated=True)
    nearby_city_names = ndb.StringProperty(indexed=False, repeated=True)  # Unused

    nonlocal_fraction = ndb.FloatProperty(indexed=True)  # Fraction of attendees that are non-local dancers
    attendee_distance_score = ndb.FloatProperty(indexed=True)  # Some functional score of the internationality of the event's attendees

    # Things that would be nice to have in DBEvent:
    # - event privacy
    # - has image?
    # - location_name / venue name
    # - city
    # - state
    # - admin ids/names

    def is_past(self):
        return self.forced_end_time_with_tz < datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    def is_canceled(self):
        if self.web_event:
            return False
        else:
            return self.fb_event['info'].get('is_canceled')

    def get_geocode(self):
        return gmaps_api.parse_geocode(self.location_geocode)

    def has_geocode(self):
        return self.location_geocode is not None and self.location_geocode.get('status') == 'OK'

    def is_indexable(self):
        full_text = ('%s %s' % (self.name, self.description)).lower()
        if re.search(r'\bno google\b', full_text):
            return False
        # Maybe do some automatic checks in the UK for international dancers?
        return True

    @classmethod
    def get_by_ids(cls, id_list, keys_only=False):
        if not id_list:
            return []
        keys = [ndb.Key(cls, x) for x in id_list]
        if keys_only:
            return cls.query(cls.key.IN(keys)).fetch(len(keys), keys_only=True)
        else:
            return ndb.get_multi(keys)

    @property
    def is_page_owned(self):
        if self.web_event:
            return False
        else:
            return self.fb_event['info'].get('is_page_owned', None)

    @property
    def web_tz(self):
        if self.web_event:
            if 'timezone' in self.web_event:
                return pytz.timezone(self.web_event['timezone'])
            else:
                return pytz.timezone('Asia/Tokyo')
        else:
            raise ValueError("Can't get timezone offset for fb events")

    def has_content(self):
        if self.web_event:
            return True
        else:
            return self.fb_event and not self.fb_event['empty']

    @property
    def start_time_string(self):
        if self.web_event:
            return self.web_event['start_time']
        else:
            return self.fb_event['info']['start_time']

    @property
    def start_time_with_tz(self):
        dt = dateutil.parser.parse(self.start_time_string)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=pytz.utc)
        return dt

    @property
    def end_time_string(self):
        if self.web_event:
            return self.web_event['end_time']
        else:
            return self.fb_event['info'].get('end_time')

    @property
    def end_time_with_tz(self):
        if self.end_time:
            dt = dateutil.parser.parse(self.end_time_string)
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=pytz.utc)
            return dt
        else:
            return None

    @property
    def forced_end_time_with_tz(self):
        if self.end_time:
            return self.end_time_with_tz
        else:
            return self.start_time_with_tz + datetime.timedelta(hours=2)

    @property
    def event_times(self):
        if self.web_event:
            return None
        else:
            event_times = self.fb_event['info'].get('event_times')
            if event_times:
                new_event_times = []
                for event_time in event_times:
                    new_event_time = {}
                    new_event_time['start_time'] = event_time['start_time']
                    if 'end_time' in event_time:
                        new_event_time['end_time'] = event_time['end_time']
                    new_event_times.append(new_event_time)
                return new_event_times
            else:
                return None

    @property
    def ticket_uri(self):
        if self.web_event:
            return None
        else:
            return self.fb_event['info'].get('ticket_uri')

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
            description = self.web_event['description']
        else:
            description = self.fb_event['info'].get('description', '')
        # TODO: Horrible Hack. Fix and generalize this:
        if self.id == '117285065630229':
            promo_text = 'ENTER PROMO CODE "DANCEDEETS" FOR $5 OFF WHEN YOU PURCHASE THE TICKET'
            description = '%s\n\n%s' % (promo_text, description)
            description = description.replace('ask promoters for Promo Code', promo_text)
        return description

    @property
    def public(self):
        if self.web_event:
            return True
        else:
            return fb_events.is_public(self.fb_event)

    @property
    def categories(self):
        return event_types.humanize_categories(self.auto_categories)

    @property
    def has_image(self):
        return self.json_props and self.json_props.get('photo_width')

    @property
    def cover_images(self):
        if self.web_event:
            # Only return a cover image here if we have a width/height,
            # as iOS will probably crash with zero-sized width/heights
            if self.json_props and self.json_props.get('photo_width') and self.json_props.get('photo_height'):
                return [{
                    'source': self.web_event['photo'],
                    'width': self.json_props['photo_width'],
                    'height': self.json_props['photo_height'],
                }]
            elif self.web_event.get('photo_width') and self.web_event.get('photo_height'):
                return [{
                    'source': self.web_event['photo'],
                    'width': self.web_event['photo_width'],
                    'height': self.web_event['photo_height'],
                }]
            else:
                return []
        else:
            if 'cover_info' in self.fb_event:
                # Old FB API versions returned ints instead of strings, so let's stringify manually to ensure we can look up the cover_info
                fb_cover = self.fb_event['info']['cover']
                if 'id' in fb_cover:
                    # New return format
                    cover_id = fb_cover['id']
                else:
                    # Old return format that continues to live on in our data
                    cover_id = fb_cover['cover_id']
                cover = self.fb_event['cover_info'][str(cover_id)]
                return cover['images']
            else:
                return []

    def extra_image_urls(self):
        if self.web_event:
            if 'raw' in self.web_event:
                raw = self.web_event['raw']
                if 'jam_gallery' in raw:  # used by jwjam
                    image_urls = [x['pic'] for x in raw['jam_gallery']]
                    return image_urls
        return []

    @property
    def largest_cover(self):
        cover_images = self.cover_images
        if cover_images:
            return max(cover_images, key=lambda x: x['height'])
        else:
            return None

    @property
    def full_image_url(self):
        cover = self.largest_cover
        if cover:
            return cover['source']
        else:
            # Fall back to the old square images
            return self.square_image_url

    @property
    def square_image_url(self):
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
                return 'https://graph.facebook.com/%s/picture?type=%s' % (self.fb_event['info']['id'], 'large')

    @property
    def location_name(self):
        if self.web_event:
            return self.web_event.get('location_name')
        else:
            return event_locations.get_fb_place_name(self.fb_event)

    def rebuild_venue(self):
        geocode = self.get_geocode()
        return address.get_address_from_geocode(geocode)

    @property
    def venue(self):
        if self.web_event:
            return self.rebuild_venue()
        else:
            return event_locations.get_fb_place(self.fb_event) or self.rebuild_venue()

    @property
    def venue_id(self):
        if self.web_event:
            return None
        else:
            return event_locations.get_fb_place_id(self.fb_event)

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
