import logging

from google.appengine.ext import db
from google.appengine.api import datastore_errors
from google.appengine.runtime import apiproxy_errors

import datetime
import locations
import smemcache
from util import dates

USER_EXPIRY = 24 * 60 * 60

def cleanup_location(user):
    import iso3166
    if user.location is None:
        user.location = ''
        user.put()
        return
    bits = user.location.split(', ')
    if len(bits) == 3:
        if len(bits[-1]) == 2:
            country = iso3166.countries_by_alpha2.get(bits[-1])
            if country:
                bits[-1] = country.name
    bits = [x for x in bits if x != '?']
    new_location = ', '.join(bits)
    if new_location != user.location:
        user.location = new_location
        user.put()

def cleanup_location2(user):
    from util import abbrev
    import iso3166
    bits = user.location.split(', ')
    double_country = ', '.join(bits[-2:]).upper()
    if double_country in iso3166.countries_by_name:
        country = iso3166.countries_by_name[double_country.upper()]
        new_country = abbrev.countries_abbrev2full[country.alpha2]
        bits = bits[:-2] + [new_country]
    if len(bits) == 3 and len(bits[1]) == 2:
        if bits[2] not in ['United States', 'Canada']:
            bits.remove(bits[1])
    new_location = ', '.join(bits)
    print '%r -> %r' % (user.location, new_location)
    if new_location != user.location:
        user.location = new_location
        user.put()

class User(db.Model):
    # SSO
    fb_uid = property(lambda x: int(x.key().name()))
    fb_access_token = db.StringProperty(indexed=False)
    fb_access_token_expires = db.DateTimeProperty(indexed=False)

    # Statistics
    creation_time = db.DateTimeProperty()
    last_login_time = db.DateTimeProperty()
    login_count = db.IntegerProperty()
    inviting_fb_uid = db.IntegerProperty(indexed=False)

    clients = db.StringListProperty()

    # Search preferences
    location = db.StringProperty(indexed=False)
    distance = db.StringProperty(indexed=False)
    distance_units = db.StringProperty(indexed=False)
    min_attendees = db.IntegerProperty(indexed=False)

    # TODO(lambert): Get rid of these eventually??
    dance_type = db.StringProperty(indexed=False)
    freestyle = db.StringProperty(indexed=False)
    choreo = db.StringProperty(indexed=False)

    # Other preferences
    send_email = db.BooleanProperty(indexed=False)
    location_country = db.StringProperty(indexed=False)

    # Derived from fb_user
    full_name = db.StringProperty(indexed=False)
    email = db.StringProperty(indexed=False)
    timezone_offset = db.FloatProperty(indexed=False)

    expired_oauth_token = db.BooleanProperty(indexed=False)
    expired_oauth_token_reason = db.StringProperty(indexed=False)

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

    def date_only_human_format(self, d):
        return dates.date_only_human_format(d)
    def date_human_format(self, d):
        return dates.date_human_format(d, country=self.location_country)
    def duration_human_format(self, d1, d2):
        return dates.duration_human_format(d1, d2, country=self.location_country)

    def compute_derived_properties(self, fb_user):
        self.full_name = fb_user['profile']['name']
        self.email = fb_user['profile'].get('email')
        try:
            self.timezone_offset = float(fb_user['profile'].get('timezone'))
        except (datastore_errors.BadValueError, TypeError) as e:
            logging.error("Failed to save timezone %s: %s", fb_user['profile'].get('timezone'), e)
        if self.location:
            #TODO(lambert): wasteful dual-lookups, but two memcaches aren't that big a deal given how infrequently this is called
            self.location_country = locations.get_country_for_location(self.location)
        else:
            self.location_country = None

    def _populate_internal_entity(self):
        memcache_key = self.memcache_user_key(self.fb_uid)
        smemcache.set(memcache_key, self, USER_EXPIRY)
        return super(User, self)._populate_internal_entity()

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
    registered_friend_string_ids = db.StringListProperty(indexed=False)
    # deprecated
    registered_friend_ids = db.ListProperty(int, indexed=False)

class UserMessage(db.Model):
    fb_uid = db.IntegerProperty()
    creation_time = db.DateTimeProperty()
    message = db.TextProperty(indexed=False)


