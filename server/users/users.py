import logging
from timezonefinder import TimezoneFinder

from google.appengine.ext import ndb
from google.appengine.api import datastore_errors
from google.appengine.runtime import apiproxy_errors

from mapreduce import context

import datetime
import fb_api
from loc import gmaps_api
from loc import math
from mail import mailchimp_api
from util import dates
from util import mr

timezone_finder = TimezoneFinder()

class User(ndb.Model):
    # SSO
    fb_uid = property(lambda x: str(x.key.string_id()))
    fb_access_token = ndb.StringProperty(indexed=False)
    fb_access_token_expires = ndb.DateTimeProperty(indexed=False)
    expired_oauth_token = ndb.BooleanProperty()
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
    num_auto_added_events = ndb.IntegerProperty(indexed=False)
    num_auto_added_own_events = ndb.IntegerProperty(indexed=False)
    num_hand_added_events = ndb.IntegerProperty(indexed=False)
    num_hand_added_own_events = ndb.IntegerProperty(indexed=False)

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
    full_name = ndb.StringProperty() # Indexed to make it easier for me to find a user for manual support
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty() # Indexed to make it easier for me to find a user for manual support
    mailchimp_email = ndb.StringProperty() # Indexed to make it easier for me to find a user for manual support

    locale = ndb.StringProperty(indexed=False)
    timezone_offset = ndb.FloatProperty()

    weekly_email_send_date = ndb.DateTimeProperty(indexed=False)

    def get_fblookup(self):
        fbl = fb_api.FBLookup(self.fb_uid, self.fb_access_token)
        return fbl

    def dict_for_form(self):
        return {
            'location': self.location,
            #'distance': int(self.distance),
            #'distance_units': self.distance_units,
            #'min_attendees': self.min_attendees,
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
        if not self.email:
            self.email = fb_user['profile'].get('email')
        self.locale = fb_user['profile'].get('locale')
        try:
            self.timezone_offset = float(fb_user['profile'].get('timezone'))
        except (datastore_errors.BadValueError, TypeError) as e:
            logging.error("Failed to save timezone %s: %s", fb_user['profile'].get('timezone'), e)
        self.location_country = None
        if self.location:
            geocode = gmaps_api.lookup_address(self.location)
            if geocode:
                self.location_country = geocode.country()

    def put(self):
        # Always update mailchimp when we update the User
        update_mailchimp(self)
        super(User, self).put()

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


def update_mailchimp(user):
    ctx = context.get()
    mailchimp_list_id = -1
    if ctx:
        params = ctx.mapreduce_spec.mapper.params
        mailchimp_list_id = params.get('mailchimp_list_id', mailchimp_list_id)
    if mailchimp_list_id == -1:
        mailchimp_list_id = mailchimp_api.LIST_ID

    trimmed_locale = user.locale or ''
    if '_' in trimmed_locale:
        trimmed_locale = trimmed_locale.split('_')[0]

    if not user.email:
        mr.increment('mailchimp-error-no-email')
        logging.info('No email for user %s: %s', user.fb_uid, user.full_name)
        return

    if user.mailchimp_email != user.email:
        # When some old users are saved, their mailchimp email will be None,
        # so we don't really need to worry about them here.
        if user.mailchimp_email != None:
            mr.increment('mailchimp-update-email-error-response')
            try:
                result = mailchimp_api.update_email(mailchimp_api.LIST_ID, user.mailchimp_email, user.email)
            except mailchimp_api.UserNotFound:
                mr.increment('mailchimp-update-email-error-not-found')
                logging.error('Updating user %s email to mailchimp returned not found', user.fb_uid, result['errors'])
            else:
                if result['errors']:
                    mr.increment('mailchimp-update-email-error-response')
                    logging.error('Updating user %s email to mailchimp returned %s', user.fb_uid, result['errors'])
                else:
                    logging.info('Updating user %s email to mailchimp returned OK', user.fb_uid)
        # Mark our current mailchimp_email down, so we can update it properly later if desired.
        user.mailchimp_email = user.email
        # Now that Mailchimp knows about our new user email,
        # we can update/reference it using the normal add_members() below.

    member = {
        'email_address': user.email,
        # Mailchimp is the official store of 'are they subscribed', so let's not overwrite it here
        'status_if_new': 'subscribed',
        'language': trimmed_locale,
        'merge_fields': {
            'USER_ID': user.fb_uid, # necessary so we can update our local datastore on callbacks
            'FIRSTNAME': user.first_name or '',
            'LASTNAME': user.last_name or '',
            'FULLNAME': user.full_name or '',
            'NAME': user.first_name or user.full_name or '',
            'WEEKLY': unicode(user.send_email),
            'EXPIRED': unicode(user.expired_oauth_token),
            'LASTLOGIN': user.last_login_time.strftime('%Y-%m-%d') if user.last_login_time else '',
        },
        'timestamp_signup': user.creation_time.strftime('%Y-%m-%dT%H:%M:%S'),
        'timestamp_opt': user.creation_time.strftime('%Y-%m-%dT%H:%M:%S'),
    }
    if user.location:
        geocode = gmaps_api.lookup_address(user.location)
        if geocode:
            user_latlong = geocode.latlng()
            member['location'] = {
                'latitude': user_latlong[0],
                'longitude': user_latlong[1],
            }
        else:
            logging.warning('User %s (%s) had un-geocodable address: %s', user.fb_uid, user.full_name, user.location)

    mr.increment('mailchimp-api-call')
    result = mailchimp_api.add_members(mailchimp_list_id, [member])
    if result['errors']:
        mr.increment('mailchimp-error-response')
        logging.error('Writing user %s to mailchimp returned %s on input: %s', user.fb_uid, result['errors'], member)
    else:
        logging.info('Writing user %s to mailchimp returned OK', user.fb_uid)

class UserFriendsAtSignup(ndb.Model):
    fb_uid = property(lambda x: str(x.key.string_id()))
    registered_friend_string_ids = ndb.StringProperty(indexed=False, repeated=True)
    # deprecated
    registered_friend_ids = ndb.IntegerProperty(indexed=False, repeated=True)

class UserMessage(ndb.Model):
    real_fb_uid = ndb.StringProperty()
    creation_time = ndb.DateTimeProperty()
    message = ndb.TextProperty(indexed=False)
