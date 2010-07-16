from google.appengine.ext import db
import smemcache

def header_item(name, description):
    return dict(name=name, description=description)

def list_item(internal, name, description):
    return dict(internal=internal, name=name, description=description)

FREESTYLE_DANCER = 'FREESTYLE_DANCER'
FREESTYLE_FAN_WITH_CLUBS = 'FREESTYLE_FAN_WITH_CLUBS'
FREESTYLE_FAN_NO_CLUBS = 'FREESTYLE_FAN_NO_CLUBS'
FREESTYLE_APATHY = 'FREESTYLE_APATHY'

FREESTYLE_HEADER = header_item("Freestyle", "Street Dances: breaking, house dancing, popping and locking, waacking and vogue, old school hiphop, etc.")
FREESTYLE_LIST = [
    list_item(FREESTYLE_APATHY, "Freestyle Apathy", "You're not a fan of freestyle stuff, it's just not your scene."),
    list_item(FREESTYLE_FAN_NO_CLUBS, "Freestyle Fan, No Clubs", "You love watching performances, jams, and battles."),
    list_item(FREESTYLE_FAN_WITH_CLUBS, "Freestyle Fan, With Clubs", "In addition to performances, battles, and jams, you love going to the clubs to watch and absorb the vibe, even if you don't dance."),
    list_item(FREESTYLE_DANCER, "Freestyle Dancer", "Not just a fan of freestyle stuff, but a dancer as well. You're interested in workshops, practice sessions, auditions, and other venues for learning."),
]

CHOREO_DANCER = 'CHOREO_DANCER'
CHOREO_FAN = 'CHOREO_FAN'
CHOREO_APATHY = 'CHOREO_APATHY'

CHOREO_HEADER = header_item("Choreo", "Hiphop choreography, urban dance choreography, jazz-funk, contemporary hiphop, etc.")
CHOREO_LIST = [
    list_item(CHOREO_APATHY, "Choreo Apathy", "You're not a fan of hiphop choreography, it's just not your scene."),
    list_item(CHOREO_FAN, "Choreo Fan", "You love watching hiphop choreography in performances and shows, including hiphop choreography competitions."),
    list_item(CHOREO_DANCER, "Choreo Dancer", "Not just a fan, but you love hiphop workshops, auditions, and everything else in the hiphop choreography scene (also known as urban choreography scene.) This can potentially include jazz funk, hiphop/jazz, and other such blends of styles."),
]

# these must match the field names below in the User table
DANCE_CHOREO = 'choreo'
DANCE_FREESTYLE = 'freestyle'

DANCES = [DANCE_FREESTYLE, DANCE_CHOREO]
DANCE_HEADERS = {DANCE_FREESTYLE: FREESTYLE_HEADER, DANCE_CHOREO: CHOREO_HEADER}
DANCE_LISTS = {DANCE_FREESTYLE: FREESTYLE_LIST, DANCE_CHOREO: CHOREO_LIST}

USER_EXPIRY = 24 * 60 * 60

class User(db.Model):
    # SSO
    fb_uid = db.IntegerProperty()
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

    def distance_in_km(self):
        import logging
        if self.distance_units == 'km':
            return int(self.distance)
        else:
            return int(self.distance) * 1.609344

    @staticmethod
    def memcache_user_key(fb_user_id):
        return 'User.%s' % fb_user_id

    @classmethod
    def get(cls, uid, allow_memcache=True):
        memcache_key = cls.memcache_user_key(uid)
        user = allow_memcache and smemcache.get(memcache_key)
        if not user:
            fetched_users = User.gql('where fb_uid = :fb_uid', fb_uid=uid).fetch(1)
            if fetched_users:
                user = fetched_users[0]
            smemcache.set(memcache_key, user, USER_EXPIRY)
        #TODO(lambert): is this a good idea? it can construct a not-filled-out user that we may depend on later, depending on who calls this.
        if not user:
            user = User(fb_uid=uid)
        return user

    def put(self):
        super(User, self).put()
        memcache_key = self.memcache_user_key(self.fb_uid)
        smemcache.set(memcache_key, self, USER_EXPIRY)


class UserFriendsAtSignup(db.Model):
    fb_uid = db.IntegerProperty()
    registered_friend_ids = db.ListProperty(int)
