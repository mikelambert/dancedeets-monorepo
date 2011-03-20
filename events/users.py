import logging

from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

import cities
import datetime
import locations
import smemcache
from util import dates

def header_item(name, description):
    return dict(name=name, description=description)

def list_item(internal, name, description):
    return dict(internal=internal, name=name, description=description)

DANCE_TYPE_ALL_DANCE = list_item('DANCE_TYPE_ALL_DANCE', 'All Dance', '')
DANCE_TYPE_FREESTYLE = list_item('DANCE_TYPE_FREESTYLE', 'Freestyle', '')
DANCE_TYPE_CHOREO = list_item('DANCE_TYPE_CHOREO', 'Choreo', '')
DANCE_TYPE_FAN = list_item('DANCE_TYPE_FAN', 'Dance Fan', '')
DANCE_TYPES_LIST = [
    DANCE_TYPE_ALL_DANCE,
    DANCE_TYPE_FREESTYLE,
    DANCE_TYPE_CHOREO,
    DANCE_TYPE_FAN,
]

FREESTYLE_DANCER = 'FREESTYLE_DANCER'
FREESTYLE_FAN = 'FREESTYLE_FAN'
FREESTYLE_APATHY = 'FREESTYLE_APATHY'

FREESTYLE_HEADER = header_item("Freestyle", "Street Dances: breaking, house dancing, popping and locking, waacking and vogue, old school hiphop, etc.")
FREESTYLE_LIST = [
    list_item(FREESTYLE_APATHY, "No Interest in Freestyle", "You're not a fan of freestyle stuff, it's just not your scene to do yourself...yet."),
    list_item(FREESTYLE_FAN, "Fan of Freestyle", "You love watching performances, jams, and battles, but don't jump in circles yourself."),
    list_item(FREESTYLE_DANCER, "Freestyle Dancer", "Not just a fan of freestyle stuff, but a dancer as well. You're interested in workshops, practice sessions, auditions, and other venues for learning."),
]

CHOREO_DANCER = 'CHOREO_DANCER'
CHOREO_FAN = 'CHOREO_FAN'
CHOREO_APATHY = 'CHOREO_APATHY'

CHOREO_HEADER = header_item("Choreo", "Hiphop choreography, new-school hiphop, urban dance choreography, jazz-funk, contemporary hiphop, etc.")
CHOREO_LIST = [
    list_item(CHOREO_APATHY, "No Interest in Choreo", "You're not a fan of hiphop choreography, it's just not your scene to do yourself...yet."),
    list_item(CHOREO_FAN, "Fan of Choreo", "You love watching hiphop choreography in performances and shows, including hiphop choreography competitions."),
    list_item(CHOREO_DANCER, "Choreo Dancer", "Not just a fan, but you love hiphop workshops, auditions, and everything else in the hiphop choreography scene (also known as urban choreography scene.) This can potentially include jazz funk, hiphop/jazz, and other such blends of styles."),
]

# these must match the field names below in the User table
DANCE_CHOREO = 'choreo'
DANCE_FREESTYLE = 'freestyle'

DANCES = [DANCE_FREESTYLE, DANCE_CHOREO]
DANCE_HEADERS = {DANCE_FREESTYLE: FREESTYLE_HEADER, DANCE_CHOREO: CHOREO_HEADER}
DANCE_LISTS = {DANCE_FREESTYLE: FREESTYLE_LIST, DANCE_CHOREO: CHOREO_LIST}

USER_EXPIRY = 24 * 60 * 60

def time_human_format(d, user):
    if not user or user.location_country in locations.AMPM_COUNTRIES:
        time_string = '%d:%02d%s' % (int(d.strftime('%I')), d.minute, d.strftime('%p').lower())
    else:
        time_string = '%d:%02d' % (int(d.strftime('%H')), d.minute)
    return time_string

def date_human_format(d, user=None):
    month_day_of_week = d.strftime('%A, %B')
    month_day = '%s %s' % (month_day_of_week, d.day)
    time_string = time_human_format(d, user=user)
    return '%s - %s' % (month_day, time_string)

def duration_human_format(d1, d2, user=None):
    first_date = date_human_format(d1)
    if (d2 - d1) > datetime.timedelta(hours=24):
        second_date = date_human_format(d2, user)
    else:
        second_date = time_human_format(d2, user)
    
    return "%s to %s" % (first_date, second_date)

class User(db.Model):
    # SSO
    fb_uid = property(lambda x: int(x.key().name()))
    fb_access_token = db.StringProperty()

    # Statistics
    creation_time = db.DateTimeProperty()
    last_login_time = db.DateTimeProperty()
    inviting_fb_uid = db.IntegerProperty()

    # Search preferences
    location = db.StringProperty()
    distance = db.StringProperty()
    distance_units = db.StringProperty()

    dance_type = db.StringProperty()
    freestyle = db.StringProperty()
    choreo = db.StringProperty()

    # Other preferences
    send_email = db.BooleanProperty()
    location_country = db.StringProperty()
    location_timezone = db.StringProperty()

    # Derived from fb_user
    full_name = db.StringProperty()
    email = db.StringProperty()

    expired_oauth_token = db.BooleanProperty()

    def distance_in_km(self):
        if not self.distance:
            return 0
        elif self.distance_units == 'km':
            return int(self.distance)
        else:
            return locations.miles_in_km(int(self.distance))

    @staticmethod
    def memcache_user_key(fb_user_id):
        return 'User.%s' % fb_user_id

    @classmethod
    def get_cached(cls, uid):
        memcache_key = cls.memcache_user_key(uid)
        user = smemcache.get(memcache_key)
        if not user:
            user = User.get_by_key_name(str(uid))
            if user:
                smemcache.set(memcache_key, user, USER_EXPIRY)
        return user

    def compute_derived_properties(self, fb_user):
        self.full_name = fb_user['profile']['name']
        self.email = fb_user['profile'].get('email')
        if self.location:
            #TODO(lambert): wasteful dual-lookups, but two memcaches aren't that big a deal given how infrequently this is called
            self.location_country = locations.get_country_for_location(self.location)
            closest_city = cities.get_closest_city(self.location)
            if closest_city:
                self.location_timezone = closest_city.timezone
            else:
                self.location_timezone = None
        else:
            self.location_country = None
            self.location_timezone = None

    def local_time(self):
        return dates.localize_timestamp(datetime.datetime.now(), timezone_str=self.location_timezone)

    def _populate_internal_entity(self):
        logging.info("a %s" % self.dance_type)
        if not getattr(self, 'dance_type', None):
            logging.info("b")
            if self.freestyle == FREESTYLE_DANCER and self.choreo == CHOREO_DANCER:
                self.dance_type = DANCE_TYPE_ALL_DANCE['internal']
            elif self.freestyle == FREESTYLE_DANCER:
                self.dance_type = DANCE_TYPE_FREESTYLE['internal']
            elif self.choreo == CHOREO_DANCER:
                self.dance_type = DANCE_TYPE_CHOREO['internal']
            else:
                self.dance_type = DANCE_TYPE_FAN['internal']
        logging.info("c %s" % self.dance_type)
        memcache_key = self.memcache_user_key(self.fb_uid)
        smemcache.set(memcache_key, self, USER_EXPIRY)
        return super(User, self)._populate_internal_entity()

    def get_city(self):
        if self.location:
            #TODO(lambert): cache this user city!
            user_city = cities.get_largest_nearby_city_name(self.location)
            return user_city
        else:
            return None

    def add_message(self, message):
        user_message = UserMessage(
            fb_uid=self.fb_uid,
            creation_time=datetime.datetime.now(),    
            message=message,
        )
        try:
            user_message.put()
        except apiproxy_errors.CapabilityDisabledError:
            pass
        return user_message

    def get_and_purge_messages(self):
        user_messages = UserMessage.gql("WHERE fb_uid = :fb_uid ORDER BY creation_time", fb_uid=self.fb_uid).fetch(100)
        messages = [x.message for x in user_messages]
        for user_message in user_messages:
            user_message.delete()
        return messages

class UserFriendsAtSignup(db.Model):
    fb_uid = property(lambda x: int(x.key().name()))
    registered_friend_ids = db.ListProperty(int)

class UserMessage(db.Model):
    fb_uid = db.IntegerProperty()
    creation_time = db.DateTimeProperty()
    message = db.TextProperty()


