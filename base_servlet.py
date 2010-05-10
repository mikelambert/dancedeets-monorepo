#!/usr/bin/env python

import datetime
import logging
import re
import sys

import countries
from facebook import webappfb
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from django.utils import simplejson
from util import text

MEMCACHE_EXPIRY = 3600 * 24

#TODO(lambert): force login before accessing stuff
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

class BaseRequestHandler(webappfb.FacebookRequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseRequestHandler, self).__init__(*args, **kwargs)

    def initialize(self, request, response):
        super(BaseRequestHandler, self).initialize(request, response)
        self.display = {}
        # functions, add these to some base display setup
        self.display['format_html'] = text.format_html
        self.display['date_human_format'] = self.date_human_format
        self.display['date_format'] = text.date_format
        self.display['format'] = text.format
        self.batch_lookup = BatchLookup(self.facebook)
        # Always look up the user's information for every page view...?
        self.batch_lookup.lookup_user(self.facebook.uid)

    def render_template(self, name):
        template_class = import_template_class(name)
        template = template_class(search_list=[self.display], default_filter=text.html_escape)
        self.response.out.write(template.main().strip())

    def localize_timestamp(self, dt):
        time_offset = self.batch_lookup.users[self.facebook.uid]['profile']['timezone']
        td = datetime.timedelta(hours=time_offset)
        final_dt = dt + td
        return final_dt

    def date_human_format(self, d):
        now = datetime.datetime.now()
        difference = (d - now)
        month_day_of_week = d.strftime('%A, %B')
        month_day = '%s %s' % (month_day_of_week, d.day)
        if self.user_country in countries.AMPM_COUNTRIES:
            time_string = '%d:%02d%s' % (int(d.strftime('%I')), d.minute, d.strftime('%p').lower())
        else:
            time_string = '%d:%02d' % (int(d.strftime('%H')), d.minute)
        return '%s at %s' % (month_day, time_string)

    def current_user(self):
        return self.batch_lookup.users[self.facebook.uid]

    def load_user_country(self):
        location_name = self.current_user()['profile']['location']['name']
        self.user_country = countries.get_country_for_location(location_name)

    def finish_preload(self):
        self.batch_lookup.finish_loading()
        self.load_user_country()

class BatchLookup(object):
    def __init__(self, facebook, allow_memcache=True):
        self.facebook = facebook
        self.allow_memcache = allow_memcache
        self.users = {}
        self.user_rpcs = {}
        self.events = {}
        self.event_rpcs = {}

    def _fetch_rpc(self, path):
        rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(rpc, "https://graph.facebook.com/%s?access_token=%s" % (path, self.facebook.access_token))
        return rpc

    @staticmethod
    def _memcache_user_key(user_id):
        return 'FacebookUser.%s' % user_id

    @staticmethod
    def _memcache_event_key(event_id):
        return 'FacebookEvent.%s' % event_id

    #TODO(lambert): maybe convert these into get_multis and redo the API if the need warrants it?
    def lookup_user(self, user_id):
        memcache_key = self._memcache_user_key(user_id)
        result = self.allow_memcache and memcache.get(memcache_key)
        if result:
            self.users[user_id] = result
        else:
            self.user_rpcs[user_id] = dict(
                profile=self._fetch_rpc('%s' % user_id),
                friends=self._fetch_rpc('%s/friends' % user_id),
                events=self._fetch_rpc('%s/events' % user_id)
            )

    def lookup_event(self, event_id):
        memcache_key = self._memcache_event_key(event_id)
        result = self.allow_memcache and memcache.get(memcache_key)
        if result:
            self.events[event_id] = result
        else:
            self.event_rpcs[event_id] = dict(
                info=self._fetch_rpc('%s' % event_id),
                attending=self._fetch_rpc('%s/attending' % event_id),
                maybe=self._fetch_rpc('%s/maybe' % event_id),
                declined=self._fetch_rpc('%s/declined' % event_id),
                noreply=self._fetch_rpc('%s/noreply' % event_id),
            )

    @staticmethod
    def _map_rpc_to_json(rpc):
        try:
            result = rpc.get_result()
            if result.status_code == 200:
                text = result.content
                return simplejson.loads(result.content)
        except urlfetch.DownloadError:
            pass
        return 'ERROR'

    def finish_loading(self):
        memcache_set = {}
        for user_id, user_dict in self.user_rpcs.items():
            result = dict((k, self._map_rpc_to_json(v)) for k, v in user_dict.iteritems())
            memcache_set[self._memcache_user_key(user_id)] = result
            self.users[user_id] = result
        for event_id, event_dict in self.event_rpcs.items():
            result = dict((k, self._map_rpc_to_json(v)) for k, v in event_dict.iteritems())
            memcache_key = self._memcache_event_key(event_id)
            memcache_set[_memcache_event_key(event_id)] = result
            self.events[event_id] = result
    
        if self.allow_memcache and memcache_set:
            #TODO(lambert): check if this is above 1mb, and split it if so?
            import pickle
            set_size = len(pickle.dumps(memcache_set))
            logging.info('set memcache size is %s' % set_size)
      
            memcache.set_multi(memcache_set, MEMCACHE_EXPIRY)

