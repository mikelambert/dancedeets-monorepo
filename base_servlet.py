#!/usr/bin/env python

import datetime
import logging
import pickle
import re
import sys
import time
import urllib

import facebook
import locations
from google.appengine.ext.appstats import recording
from google.appengine.ext.webapp import RequestHandler
from google.appengine.api import urlfetch
from django.utils import simplejson
from util import text
from events import users
import template
import smemcache

#TODO(lambert): set up a background cron job to refresh events, maybe use appengine data store

#TODO(lambert): show event info, queries without login?? P2

class _ValidationError(Exception):
    pass
class _ResponseComplete(Exception):
    pass

FACEBOOK_CONFIG = None

class BaseRequestHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseRequestHandler, self).__init__(*args, **kwargs)

    def initialize(self, request, response):
        super(BaseRequestHandler, self).initialize(request, response)
        args = facebook.get_user_from_cookie(request.cookies, FACEBOOK_CONFIG['api_key'], FACEBOOK_CONFIG['secret_key'])
        if args:
            self.fb_uid = int(args['uid'])
            self.fb_graph = facebook.GraphAPI(args['access_token'])
            self.user = users.User.get(self.fb_uid)
        else:
            self.fb_uid = None
            self.fb_graph = None
            self.user = None
        self.display = {}
        self._errors = []
        # We can safely do this since there are very few ways others can modify self._errors
        self.display['errors'] = self._errors
        # functions, add these to some base display setup
        self.display['format_html'] = text.format_html
        self.display['date_human_format'] = self.date_human_format
        self.display['date_format'] = text.date_format
        self.display['format'] = text.format
        self.redirecting = False
        if self.requires_login():
            if not self.fb_uid:
                self.redirect('/login?next=%s' % urllib.quote(self.request.url))
                self.redirecting = True
            else:
                self.batch_lookup = BatchLookup(self.fb_uid, self.fb_graph)
                # Always look up the user's information for every page view...?
                self.batch_lookup.lookup_user(self.fb_uid)

    def requires_login(self):
        return True

    def add_error(self, error):
        self._errors.append(error)

    def fatal_error(self, error):
        self.add_error(error)
        self.errors_are_fatal()

    def errors_are_fatal(self):
        if self._errors:
            raise ValidationError()

    def handle_exception(self, e, debug):
        if isinstance(e, _ResponseComplete):
            return
        elif isinstance(e, _ValidationError):
            self.handle_error_response(self._errors)
        else:
            super(BaseRequestHandler, self).handle_exception(e, debug)

    def handle_error_response(self, errors):
        if self.request.method == 'POST':
            self.get() # call get response handler if we have post validation errors
        else:
            response.out.write("Fatal Error in non-POST request, non-recoverable!")

    def write_json_response(self, **kwargs):
        self.response.out.write(simplejson.dumps(kwargs))

    def render_template(self, name):
        rendered = template.render_template(name, self.display)
        self.response.out.write(rendered)

    def parse_fb_timestamp(self, fb_timestamp):
        return self.localize_timestamp(datetime.datetime.strptime(fb_timestamp, '%Y-%m-%dT%H:%M:%S+0000'))

    def localize_timestamp(self, dt):
        time_offset = self.batch_lookup.data_for_user(self.fb_uid)['profile']['timezone']
        td = datetime.timedelta(hours=time_offset)
        final_dt = dt + td
        return final_dt

    def date_human_format(self, d):
        now = datetime.datetime.now()
        difference = (d - now)
        month_day_of_week = d.strftime('%A, %B')
        month_day = '%s %s' % (month_day_of_week, d.day)
        if self.user.location_country in locations.AMPM_COUNTRIES:
            time_string = '%d:%02d%s' % (int(d.strftime('%I')), d.minute, d.strftime('%p').lower())
        else:
            time_string = '%d:%02d' % (int(d.strftime('%H')), d.minute)
        return '%s at %s' % (month_day, time_string)

    def current_user(self):
        return self.batch_lookup.data_for_user(self.fb_uid)

    def finish_preload(self):
        if self.redirecting:
            raise _ResponseComplete()
        self.batch_lookup.finish_loading()

class FacebookException(Exception):
    pass

RSVP_EVENTS_FQL = """
SELECT eid, rsvp_status
FROM event_member
WHERE uid = %s
"""

# Not used
RSVP_FUTURE_EVENTS_FQL = """
SELECT eid, rsvp_status
FROM event_member
WHERE eid in 
    (SELECT eid FROM event 
    WHERE eid IN (SELECT eid FROM event_member WHERE uid = %s) 
    AND start_time > '%s' ORDER BY start_time)
"""

ALL_EVENTS_FQL = """
SELECT eid, name, start_time, end_time, host
FROM event 
WHERE eid IN (SELECT eid FROM event_member WHERE uid = %s) 
AND start_time > '%s' 
ORDER BY start_time
"""

class BatchLookup(object):
    OBJECT_USER = 'USER'
    OBJECT_EVENT = 'EVENT'
    OBJECT_EVENT_MEMBERS = 'EVENT_MEMBERS'
    OBJECT_FQL = 'FQL'

    def _memcache_key(self, object_key):
        return 'Facebook.%s.%s' % (self.fb_uid, object_key)

    def _is_cacheable(self, object_key, this_object):
        object_id, object_type = object_key
        if object_type != self.OBJECT_EVENT:
            return True
        elif  'info' in this_object and this_object['info']['privacy'] == 'OPEN':
            return True
        else:
            return False

    def _get_rpcs(self, object_key):
        object_id, object_type = object_key
        if object_type == self.OBJECT_USER:
            today = time.mktime(datetime.date.today().timetuple()[:9])
            return dict(
                profile=self._fetch_rpc('%s' % object_id),
                friends=self._fetch_rpc('%s/friends' % object_id),
                rsvp_for_events=self._fql_rpc(RSVP_EVENTS_FQL % object_id),
                all_event_info=self._fql_rpc(ALL_EVENTS_FQL % (object_id, today)),
            )
        elif object_type == self.OBJECT_EVENT:
            return dict(
                info=self._fetch_rpc('%s' % object_id),
                picture=self._fetch_rpc('%s/picture' % object_id),
            )
        elif object_type == self.OBJECT_EVENT_MEMBERS:
            return dict(
                attending=self._fetch_rpc('%s/attending' % object_id),
                maybe=self._fetch_rpc('%s/maybe' % object_id),
                declined=self._fetch_rpc('%s/declined' % object_id),
                noreply=self._fetch_rpc('%s/noreply' % object_id),
            )
        elif object_type == self.OBJECT_FQL:
            return dict(fql=self._fql_rpc(object_id))
        else:
            raise Exception("Unknown object type %s" % object_type)

    def __init__(self, fb_uid, fb_graph, allow_memcache=True):
        self.fb_uid = fb_uid
        self.fb_graph = fb_graph
        self.allow_memcache = allow_memcache
        self.object_keys = set()

    def _fql_rpc(self, fql):
        rpc = urlfetch.create_rpc()
        url = "https://api.facebook.com/method/fql.query?%s" % urllib.urlencode(dict(query=fql, access_token=self.fb_graph.access_token, format='json'))
        urlfetch.make_fetch_call(rpc, url)
        return rpc

    def _fetch_rpc(self, path):
        rpc = urlfetch.create_rpc()
        url = "https://graph.facebook.com/%s?access_token=%s" % (path, self.fb_graph.access_token)
        urlfetch.make_fetch_call(rpc, url)
        return rpc

    def lookup_user(self, user_id):
        assert user_id
        self.object_keys.add((user_id, self.OBJECT_USER))

    def lookup_event(self, event_id):
        assert event_id
        self.object_keys.add((event_id, self.OBJECT_EVENT))

    def lookup_event_members(self, event_id):
        assert event_id
        self.object_keys.add((event_id, self.OBJECT_EVENT_MEMBERS))

    def lookup_fql(self, fql_query):
        assert fql_query
        self.object_keys.add((fql_query, self.OBJECT_FQL))

    def data_for_user(self, user_id):
        assert user_id
        return self.objects[(user_id, self.OBJECT_USER)]

    def data_for_event(self, event_id):
        assert event_id
        return self.objects[(event_id, self.OBJECT_EVENT)]

    def data_for_event_members(self, event_id):
        assert event_id
        return self.objects[(event_id, self.OBJECT_EVENT_MEMBERS)]

    def data_for_fql(self, fql_query):
        assert fql_query
        return self.objects[(fql_query, self.OBJECT_FQL)]

    def _get_objects_from_memcache(self, object_keys):
        memcache_keys_to_ids = {}
        memcache_keys_to_object_keys = dict((self._memcache_key(object_key), object_key) for object_key in object_keys)
        memcache_keys_to_objects = smemcache.get_multi(memcache_keys_to_object_keys.keys())

        objects = dict((memcache_keys_to_object_keys[k], o) for (k, o) in memcache_keys_to_objects.iteritems())

        get_size = len(pickle.dumps(memcache_keys_to_objects))
        logging.info("BatchLookup: get_multi return size: %s", get_size)
        logging.info("BatchLookup: get_multi objects: %s", objects.keys())
        return objects

    def finish_loading(self):
        if self.allow_memcache:
            self.objects = self._get_objects_from_memcache(self.object_keys)
            object_keys_to_lookup = list(set(self.object_keys).difference(self.objects.keys()))
            logging.info("BatchLookup: get_multi missed objects: %s", object_keys_to_lookup)
        else:
            object_keys_to_lookup = list(self.object_keys)

        FB_FETCH_COUNT = 10 # number of objects, each of which may be 1-5 RPCs
        for i in range(0, len(object_keys_to_lookup), FB_FETCH_COUNT):
            fetched_objects = self._fetch_object_keys(object_keys_to_lookup[i:i+FB_FETCH_COUNT])    
            # Always store latest fetched stuff in memcache, regardless of self.allow_memcache
            self._store_objects_into_memcache(fetched_objects)
            self.objects.update(fetched_objects)

    @classmethod
    def _map_rpc_to_data(cls, object_key, object_rpc_name, object_rpc):
        object_id, object_type = object_key
        try:
            result = object_rpc.get_result()
            if result.status_code == 200:
                if object_type == cls.OBJECT_EVENT and object_rpc_name == 'picture':
                    return result.final_url
                else:
                    text = result.content
                    return simplejson.loads(text)
        except urlfetch.DownloadError:
            logging.error("Error downloading: %s", object_rpc.request.url())
        return None

    def _fetch_object_keys(self, object_keys_to_lookup):
        logging.info("Looking up IDs: %s", object_keys_to_lookup)
        # initiate RPCs
        self.object_keys_to_rpcs = {}
        for object_key in object_keys_to_lookup:
            self.object_keys_to_rpcs[object_key] = self._get_rpcs(object_key)
    
        # fetch RPCs
        fetched_objects = {}
        for object_key, object_rpc_dict in self.object_keys_to_rpcs.iteritems():
            this_object = {}
            object_is_bad = False
            for object_rpc_name, object_rpc in object_rpc_dict.iteritems():
                object_json = self._map_rpc_to_data(object_key, object_rpc_name, object_rpc)
                if object_json:
                    this_object[object_rpc_name] = object_json
                else:
                    object_is_bad = True
            if object_is_bad:
                logging.error("Failed to complete object: %s, only have keys %s", object_key, this_object.keys())
            else:
                fetched_objects[object_key] = this_object

        return fetched_objects

    def _store_objects_into_memcache(self, fetched_objects):
        memcache_set = {}
        for object_key, this_object in fetched_objects.iteritems():
            if self._is_cacheable(object_key, this_object):
                memcache_set[self._memcache_key(object_key)] = this_object

        if memcache_set:
            for (k, v) in memcache_set.iteritems():
                smemcache.set(k, v, smemcache.expiry_with_variance(smemcache.MEMCACHE_EXPIRY, smemcache.MEMCACHE_VARIANCE))
            # Doesn't allow any variation between object expiries
            #smemcache.safe_set_memcache(memcache_set, smemcache.MEMCACHE_EXPIRY)
