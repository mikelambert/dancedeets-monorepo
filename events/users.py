import cities
import datetime
from google.appengine.ext import db
import locations
import smemcache
from util import timezones

def header_item(name, description):
    return dict(name=name, description=description)

def list_item(internal, name, description):
    return dict(internal=internal, name=name, description=description)

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

def get_location(fb_user):
    if fb_user['profile'].get('location'):
        facebook_location = fb_user['profile']['location']['name']
    else:
        facebook_location = None
    return facebook_location

class User(db.Model):
    # SSO
    fb_uid = property(lambda x: int(x.key().name()))
    fb_access_token = db.StringProperty()

    # Statistics
    creation_time = db.DateTimeProperty()

    # Search preferences
    location = db.StringProperty()
    distance = db.StringProperty()
    distance_units = db.StringProperty()
    freestyle = db.StringProperty()
    choreo = db.StringProperty()

    # Other preferences
    send_email = db.BooleanProperty()
    location_country = db.StringProperty()
    location_timezone = db.StringProperty()

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
    def get(cls, uid, allow_memcache=True):
        memcache_key = cls.memcache_user_key(uid)
        user = allow_memcache and smemcache.get(memcache_key)
        if not user:
            user = User.get_by_key_name(str(uid))
            smemcache.set(memcache_key, user, USER_EXPIRY)
        return user

    @classmethod
    def get_default_user(cls, fb_uid, location):
        user = User(key_name=str(fb_uid))
        user.location = location
        if user.location:
            state, country = locations.get_country_and_state_for_location(user.location)
            user.location_country = country
            user.location_timezone = timezones.get_timezone_for_state(state)
        else:
            user.location_country = None
            user.location_timezone = None
        user.freestyle = FREESTYLE_DANCER
        user.choreo = CHOREO_DANCER
        user.send_email = True
        if user.location_country in locations.MILES_COUNTRIES:
            user.distance = '90'
            user.distance_units = 'miles'
        else:
            user.distance = '150'
            user.distance_units = 'km'
        return user

    def put(self):
        super(User, self).put()
        memcache_key = self.memcache_user_key(self.fb_uid)
        smemcache.set(memcache_key, self, USER_EXPIRY)

    def date_human_format(self, d):
        now = datetime.datetime.now()
        difference = (d - now)
        month_day_of_week = d.strftime('%A, %B')
        month_day = '%s %s' % (month_day_of_week, d.day)
        if self.location_country in locations.AMPM_COUNTRIES:
            time_string = '%d:%02d%s' % (int(d.strftime('%I')), d.minute, d.strftime('%p').lower())
        else:
            time_string = '%d:%02d' % (int(d.strftime('%H')), d.minute)
        return '%s at %s' % (month_day, time_string)

    def get_closest_city(self):
        user_city = cities.get_closest_city(self.location)
        return user_city


class UserFriendsAtSignup(db.Model):
    fb_uid = property(lambda x: int(x.key().name()))
    registered_friend_ids = db.ListProperty(int)
