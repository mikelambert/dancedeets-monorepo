import logging

from google.appengine.ext import ndb
from google.appengine.api import datastore_errors
from google.appengine.runtime import apiproxy_errors

import datetime
import fb_api
from loc import gmaps_api
from loc import math
from util import dates

class User(ndb.Model):
    # SSO
    fb_uid = property(lambda x: str(x.key.string_id()))
    fb_access_token = ndb.StringProperty(indexed=False)
    fb_access_token_expires = ndb.DateTimeProperty(indexed=False)
    expired_oauth_token = ndb.BooleanProperty(indexed=False)
    expired_oauth_token_reason = ndb.StringProperty(indexed=False)

    # Statistics
    creation_time = ndb.DateTimeProperty()
    last_login_time = ndb.DateTimeProperty()
    login_count = ndb.IntegerProperty()
    #STR_ID_MIGRATE
    inviting_fb_uid = ndb.IntegerProperty(indexed=False)

    clients = ndb.StringProperty(indexed=False, repeated=True)

    json_data = ndb.JsonProperty()

    # Event stats
    num_auto_added_events = ndb.IntegerProperty()
    num_auto_added_own_events = ndb.IntegerProperty()
    num_hand_added_events = ndb.IntegerProperty()
    num_hand_added_own_events = ndb.IntegerProperty()

    # Search preferences
    location = ndb.StringProperty(indexed=False)
    distance = ndb.StringProperty(indexed=False) # WHY NOT INT???
    distance_units = ndb.StringProperty(indexed=False)
    min_attendees = ndb.IntegerProperty(indexed=False)

    # TODO(lambert): Get rid of these eventually??
    dance_type = ndb.StringProperty(indexed=False)
    freestyle = ndb.StringProperty(indexed=False)
    choreo = ndb.StringProperty(indexed=False)

    # Other preferences
    send_email = ndb.BooleanProperty(indexed=False)
    location_country = ndb.StringProperty(indexed=False)

    # Derived from fb_user
    full_name = ndb.StringProperty(indexed=False)
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    locale = ndb.StringProperty(indexed=False)
    timezone_offset = ndb.FloatProperty(indexed=False)

    weekly_email_send_date = ndb.DateTimeProperty(indexed=False)

    def get_fblookup(self):
        fbl = fb_api.FBLookup(self.fb_uid, self.fb_access_token)
        return fbl

    def dict_for_form(self):
        return {
            'location': self.location,
            'distance': int(self.distance),
            'distance_units': self.distance_units,
            'min_attendees': self.min_attendees,
        }

    def distance_in_km(self):
        if not self.distance:
            return 0
        elif self.distance_units == 'miles':
            return math.miles_in_km(int(self.distance))
        else:
            return int(self.distance)

    def date_only_human_format(self, d):
        return dates.date_only_human_format(d)
    def date_human_format(self, d):
        return dates.date_human_format(d, country=self.location_country)
    def time_human_format(self, d):
        return dates.time_human_format(d, country=self.location_country)
    def duration_human_format(self, d1, d2):
        return dates.duration_human_format(d1, d2, country=self.location_country)

    def compute_derived_properties(self, fb_user):
        self.full_name = fb_user['profile'].get('name')
        self.first_name = fb_user['profile'].get('first_name')
        self.last_name = fb_user['profile'].get('last_name')
        self.email = fb_user['profile'].get('email')
        self.locale = fb_user['profile'].get('locale')
        try:
            self.timezone_offset = float(fb_user['profile'].get('timezone'))
        except (datastore_errors.BadValueError, TypeError) as e:
            logging.error("Failed to save timezone %s: %s", fb_user['profile'].get('timezone'), e)
        self.location_country = None
        if self.location:
            geocode = gmaps_api.get_geocode(address=self.location)
            if geocode:
                self.location_country = geocode.country()

    def add_message(self, message):
        user_message = UserMessage(
            real_fb_uid=self.fb_uid,
            creation_time=datetime.datetime.now(),    
            message=message,
        )
        try:
            user_message.put()
        except apiproxy_errors.CapabilityDisabledError:
            pass
        return user_message

    def get_and_purge_messages(self):
        user_messages = UserMessage.query(UserMessage.real_fb_uid == self.fb_uid).order(UserMessage.creation_time).fetch(100)
        messages = [x.message for x in user_messages]
        for user_message in user_messages:
            user_message.key.delete()
        return messages

    @classmethod
    def get_by_ids(cls, id_list, keys_only=False):
        if not id_list:
            return []
        keys = [ndb.Key(cls, x) for x in id_list]
        if keys_only:
            return cls.query(cls.key.IN(keys)).fetch(len(keys), keys_only=True)
        else:
            return ndb.get_multi(keys)

    def device_tokens(self, platform):
        if platform not in ['ios', 'android']:
            raise ValueError('invalid platform: %r' % platform)
        device_tokens = (self.json_data or {}).setdefault('%s_device_token' % platform, [])
        return device_tokens

class UserFriendsAtSignup(ndb.Model):
    fb_uid = property(lambda x: str(x.key.string_id()))
    registered_friend_string_ids = ndb.StringProperty(indexed=False, repeated=True)
    # deprecated
    registered_friend_ids = ndb.IntegerProperty(indexed=False, repeated=True)

class UserMessage(ndb.Model):
    real_fb_uid = ndb.StringProperty()
    creation_time = ndb.DateTimeProperty()
    message = ndb.TextProperty(indexed=False)


