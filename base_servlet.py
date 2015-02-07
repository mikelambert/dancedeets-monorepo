#!/usr/bin/env python

import base64
import Cookie
import datetime
import json
import logging
import hashlib
import os
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.ext import deferred

from events import users
import facebook
import fb_api
from logic import backgrounder
from logic import user_creation
from logic import mobile
from logic import rankings
from logic import search_base
import template
from util import abbrev
from util import dates
from util import text
from util import urls

class _ValidationError(Exception):
    pass


class BareBaseRequestHandler(webapp2.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.display = {}
        self._errors = []

        self.display['version'] = os.getenv('CURRENT_VERSION_ID').split('.')[-1]
        # We can safely do this since there are very few ways others can modify self._errors
        self.display['errors'] = self._errors
        # functions, add these to some base display setup
        self.display['html_escape'] = text.html_escape
        self.display['truncate'] = lambda text, length: text[:length]
        self.display['format_html'] = text.format_html
        self.display['linkify'] = text.linkify
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
        for arg in sorted(self.request.GET):
            logging.info("query %r = %r", arg, self.request.GET.getall(arg))

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

def generate_userlogin_hash(user_login_cookie):
    raw_string = ','.join('%r: %r' % (k.encode('ascii'), v.encode('ascii')) for (k, v) in sorted(user_login_cookie.items()) if k != 'hash')
    m = hashlib.md5()
    m.update(facebook.FACEBOOK_CONFIG['secret_key'])
    m.update(raw_string)
    m.update(facebook.FACEBOOK_CONFIG['secret_key'])
    return m.hexdigest()

def validate_hashed_userlogin(user_login_cookie):
    passed_hash = user_login_cookie['hash']
    computed_hash = generate_userlogin_hash(user_login_cookie)
    if passed_hash != computed_hash:
        logging.error("For user_login_data %s, passed_in_hash %s != computed_hash %s", user_login_cookie, passed_hash, computed_hash)
    return passed_hash == computed_hash

def get_location(fb_user):
    if fb_user['profile'].get('location'):
        facebook_location = fb_user['profile']['location']['name']
    else:
        facebook_location = None
    return facebook_location


class BaseRequestHandler(BareBaseRequestHandler):

    def get_location_from_headers(self):
        iso3166_country = self.request.headers.get("X-AppEngine-Country")
        full_country = abbrev.countries_abbrev2full.get(iso3166_country, iso3166_country)

        location_components = []
        location_components.append(self.request.headers.get("X-AppEngine-City"))
        if full_country in ['United States', 'Canada']:
            location_components.append(self.request.headers.get("X-AppEngine-Region"))
        location_components.append(full_country)
        location = ', '.join(x for x in location_components if x and x != '?')
        return location

    def get_long_lived_token_and_expires(self, request):
        response = facebook.get_user_from_cookie(request.cookies)
        return response['access_token'], response['access_token_expires']

    def setup_login_state(self, request):
        #TODO(lambert): change fb api to not request access token, and instead pull it from the user
        # only request the access token from FB when it's been longer than a day, and do it out-of-band to fetch-and-update-db-and-memcache

        self.fb_uid = None
        self.user = None
        self.access_token = None

        if len(request.get_all('nt')) > 1:
            logging.error('Have too many nt= parameters, something is Very Wrong!')
            for k, v in request.cookies.iteritems():
                logging.info("DEBUG: cookie %r = %r", k, v)
        # Load Facebook cookie
        response = facebook.parse_signed_request_cookie(request.cookies)
        fb_cookie_uid = None
        if response:
            fb_cookie_uid = int(response['user_id'])
        logging.info("fb cookie id is %s", fb_cookie_uid)

        # Load our dancedeets logged-in user/state
        our_cookie_uid = None
        user_login_string = request.cookies.get('user_login', '')
        if user_login_string:
            user_login_cookie = json.loads(urllib.unquote(user_login_string))
            if validate_hashed_userlogin(user_login_cookie):
                our_cookie_uid = int(user_login_cookie['uid'])

        # If the user has changed facebook users, let's automatically re-login at dancedeets
        if fb_cookie_uid and fb_cookie_uid != our_cookie_uid:
            user_login_cookie = {
                'uid': str(fb_cookie_uid),
            }
            user_login_cookie['hash'] = generate_userlogin_hash(user_login_cookie)
            user_login_string = urllib.quote(json.dumps(user_login_cookie))
            logging.info("setting cookie response... to %s", user_login_string)
            domain = request.host.replace('www.','.')
            if ':' in domain:
                domain = domain.split(':')[0]
            #TODO: set_cookie() got an unexpected keyword argument 'expires'
            self.response.set_cookie('user_login', user_login_string, max_age=30*24*60*60, path='/', domain=domain)
            our_cookie_uid = fb_cookie_uid

        # Don't force-logout the user if there is a our_cookie_uid but not a fb_cookie_uid
        # The fb cookie probably expired after a couple hours, and we'd prefer to keep our users logged-in

        # Logged-out view, just return without setting anything up
        if not our_cookie_uid:
            return

        self.fb_uid = our_cookie_uid
        self.user = users.User.get_cached(str(self.fb_uid))

        # If we have a user, grab the access token
        if self.user:
            if fb_cookie_uid:
                # Long-lived tokens should last "around" 60 days, so let's refresh-renew if there's only 40 days left
                if self.user.fb_access_token_expires:
                    token_expires_soon = (self.user.fb_access_token_expires - datetime.datetime.now()) < datetime.timedelta(days=40)
                else:
                    # These are either infinite-access tokens (which won't expire soon)
                    # or they are ancient tokens (in which case, our User reload mapreduce has already set user.expired_oauth_token)
                    token_expires_soon = False
                if self.user.expired_oauth_token or token_expires_soon:
                    try:
                        access_token, access_token_expires = self.get_long_lived_token_and_expires(request)
                        logging.info("New access token from cookie: %s, expires %s", access_token, access_token_expires)
                        if access_token:
                            self.user = users.User.get_by_key_name(str(self.fb_uid))
                            self.user.fb_access_token = access_token
                            self.user.fb_access_token_expires = access_token_expires
                            self.user.expired_oauth_token = False
                            self.user.expired_oauth_token_reason = ""
                            self.user.put() # this also sets to memcache
                            logging.info("Stored the new access_token to the User db")
                        else:
                            logging.error("Got a cookie, but no access_token. Using the one from the existing user. Strange!")
                    except facebook.AlreadyHasLongLivedToken:
                        logging.info("Already have long-lived token, FB wouldn't give us a new one, so no need to refresh anything.")
                if 'web' not in self.user.clients:
                    self.user = users.User.get_by_key_name(str(self.fb_uid))
                    self.user.clients.append('web')
                    self.user.put()
                    logging.info("Added the web client to the User db")
                self.access_token = self.user.fb_access_token
            else:
                self.access_token = self.user.fb_access_token
                logging.info("Have dd login cookie but no fb login cookie")
                if self.user.expired_oauth_token:
                    self.fb_uid = None
                    self.user = None
                    self.access_token = None
                    return
        elif fb_cookie_uid:
            # if we don't have a user but do have a token, the user has granted us permissions, so let's construct the user now
            try:
                access_token, access_token_expires = self.get_long_lived_token_and_expires(request)
            except facebook.AlreadyHasLongLivedToken:
                logging.warning("Don't have user, just fb_cookie_id. And unable to get long lived token for the incoming request. Giving up and doing logged-out")
                self.fb_uid = None
                self.access_token = None
                self.user = None
                return
            self.access_token = access_token
            # Fix this ugly import hack:
            fbl = fb_api.FBLookup(self.fb_uid, self.access_token)
            fbl.debug = 'fbl' in self.debug_list
            fb_user = fbl.get(fb_api.LookupUser, self.fb_uid)
            
            referer = self.get_cookie('User-Referer')
            city = self.request.get('city') or self.get_location_from_headers() or get_location(fb_user)
            logging.info("User passed in a city of %r, facebook city is %s", self.request.get('city'), get_location(fb_user))
            user_creation.create_user_with_fbuser(self.fb_uid, fb_user, self.access_token, access_token_expires, city, send_email=True, referer=referer, client='web')
            #TODO(lambert): handle this MUUUCH better
            logging.info("Not a /login request and there is no user object, constructed one realllly-quick, and continuing on.")
            self.user = users.User.get_cached(str(self.fb_uid))
            # Should not happen:
            if not self.user:
                logging.error("We still don't have a user!")
                self.fb_uid = None
                self.access_token = None
                self.user = None
                return
        else:
            # no user, no fb_cookie_uid, but we have fb_uid from the user_login cookie
            logging.error("We have a user_login cookie, but no user, and no fb_cookie_uid. Acting as logged-out")
            self.fb_uid = None
            self.access_token = None
            self.user = None
            return

        logging.info("Logged in uid %s with name %s and token %s", self.fb_uid, self.user.full_name, self.access_token)
        
        # Track last-logged-in state
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        if not getattr(self.user, 'last_login_time', None) or self.user.last_login_time < yesterday:
            # Do this in a separate request so we don't increase latency on this call
            deferred.defer(update_last_login_time, self.user.fb_uid, datetime.datetime.now(), _queue='slow-queue')
            backgrounder.load_users([self.fb_uid], allow_cache=False)

    def initialize(self, request, response):
        super(BaseRequestHandler, self).initialize(request, response)
        self.run_handler = True
        current_url_args = {}
        for arg in sorted(self.request.GET):
            current_url_args[arg] = [x.encode('utf-8') for x in self.request.GET.getall(arg)]
        final_url = self.request.path + '?' + urllib.urlencode(current_url_args, doseq=True)
        params = dict(next=final_url)
        if 'deb' in self.request.arguments():
            params['deb'] = self.request.get('deb')
            self.debug_list = self.request.get('deb').split(',')
        else:
            self.debug_list = []
        logging.info("Debug list is %r", self.debug_list)
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
            allow_cache = bool(int(self.request.get('allow_cache', 1)))
            self.fbl = fb_api.FBLookup(self.fb_uid, self.access_token)
            self.fbl.allow_cache = allow_cache
            # Always look up the user's information for every page view...?
            self.fbl.request(fb_api.LookupUser, self.fb_uid)
        else:
            self.fbl = fb_api.FBLookup(None, None)
        self.fbl.debug = 'fbl' in self.debug_list
        if self.user:
            self.display['date_only_human_format'] = self.user.date_only_human_format
            self.display['date_human_format'] = self.user.date_human_format
            self.display['duration_human_format'] = self.user.duration_human_format
            self.display['messages'] = self.user.get_and_purge_messages()
        else:
            self.display['date_only_human_format'] = dates.date_only_human_format
            self.display['date_human_format'] = dates.date_human_format
            self.display['duration_human_format'] = dates.duration_human_format
            self.display['login_url'] = login_url

        self.display['fb_event_url'] = urls.fb_event_url
        self.display['raw_fb_event_url'] = urls.raw_fb_event_url
        self.display['dd_admin_event_url'] = urls.dd_admin_event_url
        self.display['dd_admin_source_url'] = urls.dd_admin_source_url

        self.display['request'] = request
        self.display['app_id'] = facebook.FACEBOOK_CONFIG['app_id']
        self.display['prod_mode'] = self.request.app.prod_mode
        self.display['base_hostname'] = 'dancedeets.com' if self.request.app.prod_mode else 'dev.dancedeets.com'
        self.display['full_hostname'] = 'www.dancedeets.com' if self.request.app.prod_mode else 'dev.dancedeets.com'

        # TODO: get rid of user_location when we can switch to IP-based geocoding (since mobile clients don't need it)
        # TODO(FB2.0): get rid of user_groups/user_likes
        # TODO(FB2.0): get rid of friends_events (when we have enough users using mobile 2.0 to keep us going)
        fb_permissions = 'user_location,rsvp_event,email,user_events,user_groups,user_likes,friends_events'
        if self.request.get('all_access'):
            fb_permissions += ',read_friendlists,manage_pages'
        self.display['fb_permissions'] = fb_permissions

        already_used_mobile = self.user and ('android' in self.user.clients or 'ios' in self.user.clients)
        currently_on_mobile = mobile.get_mobile_platform(self.request.user_agent)
        show_mobile_promo = not currently_on_mobile and not already_used_mobile
        self.display['show_mobile_promo'] = show_mobile_promo

        self.display['defaults'] = search_base.FrontendSearchQuery()
        self.display['defaults'].location = self.request.get('location')
        self.display['defaults'].keywords = self.request.get('keywords')
        self.display['defaults'].deb = self.request.get('deb')

        self.display['deb'] = self.request.get('deb')

        self.display.update(rankings.retrieve_summary())

    def dispatch(self):
        if self.run_handler:
            super(BaseRequestHandler, self).dispatch()

    def requires_login(self):
        return True

    def is_login_page(self):
        return False

    def finish_preload(self):
        self.fbl.batch_fetch()

    def render_template(self, name):
        # If we didn't load the user for some reason, let's load things now
        self.finish_preload()
        if self.fb_uid:
            self.display['fb_user'] = self.fbl.fetched_data(fb_api.LookupUser, self.fb_uid)
        super(BaseRequestHandler, self).render_template(name)


def update_last_login_time(user_id, login_time):
    def _update_last_login_time():
        user = users.User.get_by_key_name(str(user_id))
        user.last_login_time = login_time
        if user.login_count:
            user.login_count += 1
        else:
            user.login_count = 2 # once for this one, once for initial creation
        # in read-only, keep trying until we succeed
        user.put()
    db.run_in_transaction(_update_last_login_time)

