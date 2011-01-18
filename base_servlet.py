#!/usr/bin/env python

import base64
import Cookie
import datetime
import logging
import re
import sys
import urllib

from google.appengine.ext.webapp import RequestHandler
from django.utils import simplejson

from events import users
import facebook
import fb_api
import locations
from logic import backgrounder
import template
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

    def set_cookie(self, name, value, expires=None):
        cookie = Cookie.SimpleCookie()
        cookie[name] = str(base64.b64encode(value))
        cookie[name]['path'] = '/'
        cookie[name]['secure'] = ''
        assert not expires
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
        params = dict(next=self.request.url)
        login_url = '/login?%s' % urllib.urlencode(params)
        args = facebook.get_user_from_cookie(request.cookies, FACEBOOK_CONFIG['api_key'], FACEBOOK_CONFIG['secret_key'])
        logging.info("fb cookie is %s with args %s", request.cookies.get('fbs_' + FACEBOOK_CONFIG['api_key']), args)
        if args:
            self.fb_uid = int(args['uid'])
            self.fb_graph = facebook.GraphAPI(args['access_token'])
            self.user = users.User.get_cached(self.fb_uid)
            if self.request.path != '/login' and not self.user:
                logging.info("Not a /login request and there is no user object, so pretending they are not logged in.")
                self.fb_uid = None
            else:
                logging.info("Logged in uid %s", self.fb_uid)
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
                    backgrounder.update_last_login_time(self.fb_uid)
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
                self.set_cookie('fbs_' + FACEBOOK_CONFIG['api_key'], '')
                logging.info("clearing cookie %s", 'fbs_' + FACEBOOK_CONFIG['api_key'])
                self.set_cookie('User-Message', "You changed your facebook password, so will need to click login again.")
            if self.request.get('referer'):
                self.set_cookie('User-Referer', self.request.get('referer'))
            logging.info("Login required, redirecting to login page: %s", login_url)
            self.redirect(login_url)
            return True
        # If they have a fb_uid, let's do lookups on that behalf (does not require a user)
        if self.fb_uid:
            self.batch_lookup = fb_api.CommonBatchLookup(self.fb_uid, self.fb_graph)
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
            self.display['date_human_format'] = lambda x: users.date_human_format(x, user=self.user)
            self.display['messages'] = self.user.get_and_purge_messages()
        else:
            self.display['date_human_format'] = users.date_human_format
            self.display['login_url'] = login_url
        self.display['fb_event_url'] = urls.fb_event_url
        self.display['raw_fb_event_url'] = urls.raw_fb_event_url
        self.display['request'] = request
        self.display['api_key'] = FACEBOOK_CONFIG['api_key']
        self.display['prod_mode'] = self.prod_mode
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

