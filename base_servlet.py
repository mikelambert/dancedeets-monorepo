#!/usr/bin/env python

import datetime
import logging
import pickle
import re
import sys
import urllib

import facebook
import locations
from google.appengine.ext.appstats import recording
from google.appengine.ext.webapp import RequestHandler
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from django.utils import simplejson
from util import text
from events import users

MEMCACHE_EXPIRY = 24 * 60 * 60

#TODO(lambert): show event info, queries without login?? P2

def import_template_module(template_name):
    try:
        return sys.modules[template_name]
    except KeyError:
        __import__(template_name, globals(), locals(), [])
        return sys.modules[template_name]

def import_template_class(template_name):
    template_module = import_template_module(template_name)
    classname = template_name.split('.')[-1]
    return getattr(template_module, classname)

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
            self.user = users.get_user(self.fb_uid)
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
        template_name = 'events.compiled_templates.%s' % name
        template_class = import_template_class(template_name)
        template = template_class(search_list=[self.display], default_filter=text.html_escape)
        self.response.out.write(template.main().strip())

    def parse_fb_timestamp(self, fb_timestamp):
        return self.localize_timestamp(datetime.datetime.strptime(fb_timestamp, '%Y-%m-%dT%H:%M:%S+0000'))

    def localize_timestamp(self, dt):
        time_offset = self.batch_lookup.objects[self.fb_uid]['profile']['timezone']
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
        return self.batch_lookup.objects[self.fb_uid]

    def finish_preload(self):
        if self.redirecting:
            raise _ResponseComplete()
        self.batch_lookup.finish_loading()

class FacebookException(Exception):
    pass

class BatchLookup(object):
    OBJECT_USER = 'USER'
    OBJECT_EVENT = 'EVENT'

    def _memcache_user_key(self, user_id):
        return 'FacebookUser.%s.%s' % (self.fb_uid, user_id)
    def _memcache_event_key(self, event_id):
        return 'FacebookEvent.%s.%s' % (self.fb_uid, event_id)

    def _build_user_rpcs(self, user_id):
        return dict(
            profile=self._fetch_rpc('%s' % user_id),
            friends=self._fetch_rpc('%s/friends' % user_id),
            events=self._fetch_rpc('%s/events' % user_id)
        )
    def _build_event_rpcs(self, event_id):
        return dict(
            info=self._fetch_rpc('%s' % event_id),
            picture=self._fetch_rpc('%s/picture' % event_id),
            attending=self._fetch_rpc('%s/attending' % event_id),
            maybe=self._fetch_rpc('%s/maybe' % event_id),
            declined=self._fetch_rpc('%s/declined' % event_id),
            noreply=self._fetch_rpc('%s/noreply' % event_id),
        )

    _key_generator = {
        OBJECT_USER: _memcache_user_key,
        OBJECT_EVENT: _memcache_event_key,
    }

    _rpc_generator = {
        OBJECT_USER: _build_user_rpcs,
        OBJECT_EVENT: _build_event_rpcs,
    }
    
    def __init__(self, fb_uid, fb_graph, allow_memcache=True):
        self.fb_uid = fb_uid
        self.fb_graph = fb_graph
        self.allow_memcache = allow_memcache
        self.object_ids_to_types = {}

    def _fetch_rpc(self, path):
        rpc = urlfetch.create_rpc()
        url = "https://graph.facebook.com/%s?access_token=%s" % (path, self.fb_graph.access_token)
        urlfetch.make_fetch_call(rpc, url)
        return rpc

    def lookup_user(self, user_id):
        assert user_id
        self.object_ids_to_types[user_id] = self.OBJECT_USER

    def lookup_event(self, event_id):
        assert event_id
        self.object_ids_to_types[event_id] = self.OBJECT_EVENT

    def setup_rpcs(self):
        object_ids_to_lookup = list(self.object_ids_to_types)
        if self.allow_memcache:
            memcache_keys_to_ids = {}
            for object_id, object_type in self.object_ids_to_types.iteritems():
                key_func = self._key_generator[object_type]
                memcache_keys_to_ids[key_func(self, object_id)] = object_id
            object_keys_to_objects = memcache.get_multi(memcache_keys_to_ids.keys())
            self.objects = dict((memcache_keys_to_ids[k], o) for (k, o) in object_keys_to_objects.iteritems())
            object_ids_to_lookup = set(self.object_ids_to_types).difference(self.objects.keys())
        self.object_ids_to_rpcs = {}
        for object_id in object_ids_to_lookup:
            rpc_func = self._rpc_generator[self.object_ids_to_types[object_id]]
            self.object_ids_to_rpcs[object_id] = rpc_func(self, object_id)

    @staticmethod
    def _map_rpc_to_json(rpc):
        try:
            result = rpc.get_result()
            if result.status_code == 200:
                text = result.content
                return simplejson.loads(result.content)
        except urlfetch.DownloadError:
            pass
        return None

    def finish_loading(self):
        self.setup_rpcs()
        self.parse_rpcs()

    def parse_rpcs(self):
        memcache_set = {}
        for object_id, object_rpc_dict in self.object_ids_to_rpcs.iteritems():
            this_object = {}
            object_type = self.object_ids_to_types[object_id]
            for object_rpc_name, object_rpc in object_rpc_dict.iteritems():
                if object_type == self.OBJECT_EVENT and object_rpc_name == 'picture':
                    object_json = object_rpc.get_result().final_url
                else:
                    object_json = self._map_rpc_to_json(object_rpc)
                if object_json:
                    this_object[object_rpc_name] = object_json
            key_func = self._key_generator[object_type]
            if object_type == self.OBJECT_EVENT and this_object['info']['privacy'] == 'OPEN': # only cache the results of "open" events
                memcache_set[key_func(self, object_id)] = this_object
            self.objects[object_id] = this_object

        if self.allow_memcache and memcache_set:
            safe_set_memcache(memcache_set, MEMCACHE_EXPIRY)

def safe_set_memcache(memcache_set, expiry, top_level=True):
    set_size = len(pickle.dumps(memcache_set))
    if top_level:
        logging.info('set memcache size is %s' % set_size)
    # If it's roughly greater than a megabyte
    if set_size > 1024 * 1024 - 100:
        memcache_list = list(memcache_set.items())
        if len(memcache_list) == 1:
            logging.error("Saved item too large, cannot save, with key: %s", memcache_set.keys()[0])
            return
        halfway = len(memcache_list) / 2
        safe_set_memcache(dict(memcache_list[:halfway]), expiry, top_level=False)
        safe_set_memcache(dict(memcache_list[halfway:]), expiry, top_level=False)
    else:
        memcache.set_multi(memcache_set, MEMCACHE_EXPIRY)

