#!/usr/bin/env python

import base64
import Cookie
import datetime
import json
import logging
import os
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.ext import deferred

from events import users
import facebook
import fb_api
from logic import backgrounder
from logic import rankings
from logic import search_base
import template
from util import dates
from util import text
from util import urls

class _ValidationError(Exception):
    pass

FACEBOOK_CONFIG = None

class BareBaseRequestHandler(webapp2.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.display = {}
        self._errors = []

        self.display['version'] = os.getenv('CURRENT_VERSION_ID').split('.')[-1]
        # We can safely do this since there are very few ways others can modify self._errors
        self.display['errors'] = self._errors
        # functions, add these to some base display setup
        self.display['format_html'] = text.format_html
        self.display['format_js'] = text.format_js
        self.display['urllib_quote_plus'] = urllib.quote_plus
        self.display['urlencode'] = lambda x: urllib.quote_plus(x.encode('utf8'))

        self.display['date_format'] = text.date_format
        self.display['format'] = text.format
        self.display['next'] = ''

        # set to false on various admin pages
        self.display['track_google_analytics'] = True
        super(BareBaseRequestHandler, self).__init__(*args, **kwargs)

    def head(self):
        return self.get()

    def initialize(self, request, response):
        super(BareBaseRequestHandler, self).initialize(request, response)
        for arg in sorted(self.request.arguments()):
            logging.info("query %r = %r", arg, self.request.get_all(arg))

        logging.info("Appengine Request Headers:")
        for x in request.headers:
            if x.lower().startswith('x-appengine-'):
                logging.info("%s: %s", x, request.headers[x])

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
            raise
            #super(BareBaseRequestHandler, self).handle_exception(e, debug)

    def handle_error_response(self, errors):
        if self.request.method == 'POST':
            self.get() # call get response handler if we have post validation errors
            return True
        else:
            return False # let exception handling code operate normally

    def write_json_response(self, arg):
        self.response.out.write(json.dumps(arg))

    def render_template(self, name):
        rendered = template.render_template(name, self.display)
        self.response.out.write(rendered)

class BaseRequestHandler(BareBaseRequestHandler):
    def setup_login_state(self, request):
        #TODO(lambert): change fb api to not request access token, and instead pull it from the user
        # only request the access token from FB when it's been longer than a day, and do it out-of-band to fetch-and-update-db-and-memcache

        args = facebook.get_user_from_cookie(request.cookies, FACEBOOK_CONFIG['app_id'], FACEBOOK_CONFIG['secret_key'])
        # We should return args if we're signed in, one way or the other
        # though we may not have gotten an access_token this way if the received cookie was the same as the previous request
        if not args:
            self.fb_uid = None
            self.access_token = None
            self.user = None
            return

        self.fb_uid = int(args['uid'])
        self.user = users.User.get_cached(str(self.fb_uid))
        self.fb_user = None

        # if we don't have a user and don't have a token, it means the user just signed-up, but double-refreshed.
        # so the second request doesn't have a user. so let it be logged-out, as we continue on...
        # the other request should construct the user, so the next load should work okay
        if not self.user and not args['access_token']:
            logging.error("We have no user and no access token, but we know they're logged in. Likely due to a double-refresh on the same cookie, for a user who just signed up")
            self.fb_uid = None
            self.access_token = None
            self.user = None
            return

        # if we don't have a user but do have a token, the user has granted us permissions, so let's construct the user now
        if not self.user:
            from servlets import login
            fbl = fb_api.FBLookup(self.fb_uid, args['access_token'])
            self.fb_user = fbl.get(fb_api.LookupUser, self.fb_uid)
            
            referer = self.get_cookie('User-Referer')

            login.construct_user(self.fb_uid, args['access_token'], args['access_token_expires'], self.fb_user, self.request, referer)
            #TODO(lambert): handle this MUUUCH better
            logging.info("Not a /login request and there is no user object, constructed one realllly-quick, and continuing on.")
            self.user = users.User.get_cached(str(self.fb_uid))

        if not self.user:
            logging.error("We still don't have a user!")
            self.fb_uid = None
            self.access_token = None
            self.user = None
            return

        logging.info("Logged in uid %s with name %s", self.fb_uid, self.user.full_name)
        # When we get args, we may have gotten a new access token, or not...so choose the best we've got
        self.access_token = (args['access_token'] or (self.user and self.user.fb_access_token))
        # If their auth token has changed, then write out the new one
        logging.info("User has token %s, cookie has token %s", self.user.fb_access_token, args['access_token'])

        if (
            # if the user's token is expired and we have a new one, grab the new one
            (self.user.expired_oauth_token and args['access_token']) or
            # if the user's access token differs from what's stored, update it
            (args['access_token'] and self.user.fb_access_token != args['access_token'])
        ):
            logging.info("Putting new access token into db/memcache")
            self.user = users.User.get_by_key_name(str(self.fb_uid))
            self.user.fb_access_token = self.access_token
            self.user.expired_oauth_token = False
            self.user.put() # this also sets to memcache

        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        if not getattr(self.user, 'last_login_time', None) or self.user.last_login_time < yesterday:
            # Do this in a separate request so we don't increase latency on this call
            deferred.defer(update_last_login_time, self.user.fb_uid, datetime.datetime.now(), _queue='slow-queue')
            backgrounder.load_users([self.fb_uid], allow_cache=False)

    def initialize(self, request, response):
        super(BaseRequestHandler, self).initialize(request, response)
        self.run_handler = True
        current_url_args = {}
        for arg in sorted(self.request.arguments()):
            current_url_args[arg] = [x.encode('utf-8') for x in self.request.get_all(arg)]
        final_url = self.request.path + '?' + urllib.urlencode(current_url_args, doseq=True)
        params = dict(next=final_url)
        if 'deb' in self.request.arguments():
            params['deb'] = self.request.get('deb')
        login_url = '/login?%s' % urllib.urlencode(params)
        self.setup_login_state(request)

        self.display['attempt_autologin'] = 1
        # If they've expired, and not already on the login page, then be sure we redirect them to there...
        redirect_for_new_oauth_token = (self.user and self.user.expired_oauth_token)
        if redirect_for_new_oauth_token:
            logging.error("We have a logged in user, but an expired access token. How?!?!")
        # TODO(lambert): delete redirect_for_new_oauth_token codepaths
        # TODO(lambert): delete codepaths that handle user-id but no self.user. assume this entire thing relates to no-user.
        if redirect_for_new_oauth_token or (self.requires_login() and (not self.fb_uid or not self.user)):
            # If we're getting a referer id and not signed up, save off a cookie until they sign up
            if not self.fb_uid:
                logging.info("No facebook cookie.")
            if not self.user:
                logging.info("No database user object.")
            if self.user and self.user.expired_oauth_token:
                logging.info("User's OAuth token expired")
                #self.set_cookie('fbsr_' + FACEBOOK_CONFIG['app_id'], '', 'Thu, 01 Jan 1970 00:00:01 GMT')
                #logging.info("clearing cookie %s", 'fbsr_' + FACEBOOK_CONFIG['app_id'])
                self.set_cookie('User-Message', "You changed your facebook password, so will need to click login again.")
            if self.request.get('referer'):
                self.set_cookie('User-Referer', self.request.get('referer'))
            if not self.is_login_page():
                logging.info("Login required, redirecting to login page: %s", login_url)
                self.run_handler = False
                return self.redirect(login_url)
            else:
                self.display['attempt_autologin'] = 0 # do not attempt auto-login. wait for them to re-login
                self.fb_uid = None
                self.access_token = None
                self.user = None
        # If they have a fb_uid, let's do lookups on that behalf (does not require a user)
        if self.fb_uid:
            if not self.user:
                logging.error("Do not have a self.user at point B")
            allow_cache = bool(int(self.request.get('allow_cache', 1)))
            self.batch_lookup = fb_api.CommonBatchLookup(self.fb_uid, self.access_token, allow_cache=allow_cache)
            # Always look up the user's information for every page view...?
            self.batch_lookup.lookup_user(self.fb_uid)
        else:
            self.batch_lookup = fb_api.CommonBatchLookup(None, self.access_token)
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
        self.display['prod_mode'] = self.request.app.prod_mode

        fb_permissions = 'user_location,rsvp_event,email,user_events,user_groups,friends_events,friends_groups,user_likes,friends_likes'
        if self.request.get('all_access'):
            fb_permissions += ',read_friendlists'
        self.display['fb_permissions'] = fb_permissions

        self.display['defaults'] = search_base.FrontendSearchQuery()
        self.display['defaults'].location = self.request.get('location')
        self.display['defaults'].keywords = self.request.get('keywords')
        self.display['defaults'].deb = self.request.get('deb')

        self.display.update(rankings.retrieve_summary())
        return False

    def dispatch(self):
        if self.run_handler:
            super(BaseRequestHandler, self).dispatch()

    def requires_login(self):
        return True

    def is_login_page(self):
        return False

    def current_user(self):
        return self.fb_user

    def finish_preload(self):
        self.batch_lookup.finish_loading()

    def render_template(self, name):
        self.display['fb_user'] = self.fb_user
        super(BaseRequestHandler, self).render_template(name)


def update_last_login_time(user_id, login_time):
    def _update_last_login_time():
        user = users.User.get_by_key_name(str(user_id))
        user.last_login_time = login_time
        if getattr(user, 'login_count'):
            user.login_count += 1
        else:
            user.login_count = 2 # once for this one, once for initial creation
        # in read-only, keep trying until we succeed
        user.put()
    db.run_in_transaction(_update_last_login_time)

