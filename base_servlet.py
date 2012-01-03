#!/usr/bin/env python

import base64
import Cookie
import datetime
import logging
import re
import sys
import urllib

from google.appengine.ext import deferred
from google.appengine.ext.webapp import RequestHandler
from django.utils import simplejson

from events import users
import facebook
import fb_api
import locations
from logic import backgrounder
from logic import rankings
import template
from util import dates
from util import text
from util import urls

class _ValidationError(Exception):
    pass

FACEBOOK_CONFIG = None

class BareBaseRequestHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BareBaseRequestHandler, self).__init__(*args, **kwargs)
        self.display = {}
        self._errors = []
        # We can safely do this since there are very few ways others can modify self._errors
        self.display['errors'] = self._errors
        # functions, add these to some base display setup
        self.display['format_html'] = text.format_html
        self.display['format_js'] = text.format_js
        self.display['date_format'] = text.date_format
        self.display['format'] = text.format
        self.display['next'] = ''

    def head(self):
        return self.get()

    def initialize(self, request, response):
        super(BareBaseRequestHandler, self).initialize(request, response)
        for arg in sorted(self.request.arguments()):
            logging.info("query %r = %r", arg, self.request.get_all(arg))

    def set_cookie(self, name, value, expires=None):
        cookie = Cookie.SimpleCookie()
        cookie[name] = str(base64.b64encode(value))
        cookie[name]['path'] = '/'
        cookie[name]['secure'] = ''
        if expires is not None:
            cookie[name]['expires'] = expires
        self.response.headers.add_header(*cookie.output().split(': '))
        return cookie

    def get_cookie(self, name):
        try:
            value = str(base64.b64decode(self.request.cookies[name]))
        except KeyError:
            value = None
        return value

    def add_error(self, error):
        self._errors.append(error)

    def fatal_error(self, error):
        self.add_error(error)
        self.errors_are_fatal()

    def errors_are_fatal(self):
        if self._errors:
            raise _ValidationError(self._errors)

    def handle_exception(self, e, debug):
        handled = False
        if isinstance(e, _ValidationError):
            handled = self.handle_error_response(self._errors)
        if not handled:
            super(BareBaseRequestHandler, self).handle_exception(e, debug)

    def handle_error_response(self, errors):
        if self.request.method == 'POST':
            self.get() # call get response handler if we have post validation errors
            return True
        else:
            return False # let exception handling code operate normally

    def write_json_response(self, arg):
        self.response.out.write(simplejson.dumps(arg))

    def render_template(self, name):
        rendered = template.render_template(name, self.display)
        self.response.out.write(rendered)

class BaseRequestHandler(BareBaseRequestHandler):
    def initialize(self, request, response):
        super(BaseRequestHandler, self).initialize(request, response)
        current_url_args = {}
        for arg in sorted(self.request.arguments()):
            current_url_args[arg] = [x.encode('utf-8') for x in self.request.get_all(arg)]
        final_url = self.request.path + '?' + urllib.urlencode(current_url_args, doseq=True)
        params = dict(next=final_url)
        login_url = '/login?%s' % urllib.urlencode(params)
        args = facebook.get_user_from_cookie(request.cookies, FACEBOOK_CONFIG['app_id'], FACEBOOK_CONFIG['secret_key'])
        if args:
            self.fb_uid = int(args['uid'])
            self.fb_graph = facebook.GraphAPI(args['access_token'])
            self.user = users.User.get_cached(self.fb_uid)
            if self.request.path != '/login' and not self.user:
                logging.info("Not a /login request and there is no user object, so pretending they are not logged in.")
                self.fb_uid = None
            else:
                logging.info("Logged in uid %s with name %s", self.fb_uid, self.user and self.user.full_name)
                # If their auth token has changed, then write out the new one
                if self.request.path == '/login':
                    self.user = users.User.get_by_key_name(str(self.fb_uid))
                    if self.user:
                        self.user.fb_access_token = self.fb_graph.access_token
                        self.user.expired_oauth_token = False
                        self.user.put() # this also sets to memcache
                yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                if self.user and (not getattr(self.user, 'last_login_time', None) or self.user.last_login_time < yesterday):
                    # Do this in a separate request so we don't increase latency on this call
                    deferred.do(update_last_login_time, self.user.fb_uid, datetime.datetime.now())
                    backgrounder.load_users([self.fb_uid], allow_cache=False)
        else:
            self.fb_uid = None
            self.fb_graph = facebook.GraphAPI(None)
            self.user = None

        # If they've expired, and not already on the login page, then be sure we redirect them to there...
        redirect_for_new_oauth_token = (self.user and self.user.expired_oauth_token)
        if redirect_for_new_oauth_token or (self.requires_login() and (not self.fb_uid or not self.user)):
            # If we're getting a referer id and not signed up, save off a cookie until they sign up
            if not self.fb_uid:
                logging.info("No facebook cookie.")
            if not self.user:
                logging.info("No database user object.")
            if self.user and self.user.expired_oauth_token:
                logging.info("User's OAuth token expired")
                self.set_cookie('fbsr_' + FACEBOOK_CONFIG['app_id'], '', 0)
                logging.info("clearing cookie %s", 'fbsr_' + FACEBOOK_CONFIG['app_id'])
                self.set_cookie('User-Message', "You changed your facebook password, so will need to click login again.")
            if self.request.get('referer'):
                self.set_cookie('User-Referer', self.request.get('referer'))
            logging.info("Login required, redirecting to login page: %s", login_url)
            self.redirect(login_url)
            return True
        # If they have a fb_uid, let's do lookups on that behalf (does not require a user)
        if self.fb_uid:
            allow_cache = (self.request.get('allow_cache', '1') == '1')
            self.batch_lookup = fb_api.CommonBatchLookup(self.fb_uid, self.fb_graph, allow_cache=allow_cache)
            # Always look up the user's information for every page view...?
            self.batch_lookup.lookup_user(self.fb_uid)
        else:
            self.batch_lookup = fb_api.CommonBatchLookup(None, self.fb_graph)
        # If they've authorized us, but we don't have a User object, force them to signup so we get initial prefs
        # Let the client sit there and wait for the user to manually sign up.
        if self.fb_uid and not self.user:
            self.display['attempt_autologin'] = 0
        else:
            self.display['attempt_autologin'] = 1
        if self.user:
            self.display['date_human_format'] = self.user.date_human_format
            self.display['duration_human_format'] = self.user.duration_human_format
            self.display['messages'] = self.user.get_and_purge_messages()
        else:
            self.display['date_human_format'] = dates.date_human_format
            self.display['duration_human_format'] = dates.duration_human_format
            self.display['login_url'] = login_url

        self.display['fb_event_url'] = urls.fb_event_url
        self.display['raw_fb_event_url'] = urls.raw_fb_event_url
        self.display['dd_admin_event_url'] = urls.dd_admin_event_url
        self.display['dd_admin_source_url'] = urls.dd_admin_source_url

        self.display['request'] = request
        self.display['app_id'] = FACEBOOK_CONFIG['app_id']
        self.display['prod_mode'] = self.prod_mode

        fb_permissions = 'user_location,rsvp_event,offline_access,email,user_events,user_groups,friends_events,friends_groups,user_likes,friends_likes'
        if self.request.get('all_access'):
            fb_permissions += ',read_friendlists'
        self.display['fb_permissions'] = fb_permissions

        self.display.update(rankings.retrieve_summary())
        return False

    def requires_login(self):
        return True

    def current_user(self):
        if self.fb_uid:
            return self.batch_lookup.data_for_user(self.fb_uid)
        else:
            return None

    def finish_preload(self):
        self.batch_lookup.finish_loading()

    def render_template(self, name):
        if self.fb_uid: # show fb user if we're logged in. we only need fb_uid to get a fb_user
            self.display['fb_user'] = self.current_user()
        else:
            self.display['fb_user'] = None
        super(BaseRequestHandler, self).render_template(name)

def update_last_login_time(user_id, login_time):
    user = user = users.User.get_by_key_name(user_id)
    user.last_login_time = login_time
    if getattr(user, 'login_count'):
        user.login_count += 1
    else:
        user.login_count = 2 # once for this one, once for initial creation
    # in read-only, keep trying until we succeed
    user.put()

