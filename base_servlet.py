#!/usr/bin/env python

import base64
import Cookie
import datetime
import jinja2
import json
import htmlmin
import logging
import hashlib
import os
import urllib
import webapp2


from google.appengine.api.app_identity import app_identity
from google.appengine.ext import db
from google.appengine.ext import deferred

from users import users
import facebook
import fb_api
from logic import backgrounder
from logic import mobile
from rankings import rankings
import styles
from users import user_creation
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

        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"), autoescape=True)

        # This is necessary because appengine comes with Jinja 2.6 pre-installed, and this was added in 2.7+.
        def do_urlencode(value):
            """Escape for use in URLs."""
            return urllib.quote(value.encode('utf8'))
        self.jinja_env.filters['urlencode'] = do_urlencode
        self.jinja_env.filters['format_html'] = text.format_html
        self.jinja_env.filters['escapejs'] = text.escapejs
        self.jinja_env.globals['zip'] = zip
        self.jinja_env.globals['len'] = len

        self.display['version'] = os.getenv('CURRENT_VERSION_ID').split('.')[-1]
        # We can safely do this since there are very few ways others can modify self._errors
        self.display['errors'] = self._errors
        # functions, add these to some base display setup
        self.display['truncate'] = lambda text, length: text[:length]
        self.jinja_env.filters['format_html'] = text.format_html
        self.jinja_env.filters['linkify'] = text.linkify
        self.jinja_env.filters['format_js'] = text.format_js
        self.display['jsonify'] = json.dumps
        self.display['urllib_quote_plus'] = urllib.quote_plus
        self.display['urlencode'] = lambda x: urllib.quote_plus(x.encode('utf8'))

        self.display['date_format'] = text.date_format
        self.display['format'] = text.format
        self.display['next'] = ''

        # set to false on various admin pages
        self.display['track_google_analytics'] = True
        super(BareBaseRequestHandler, self).__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        raise NotImplementedError()

    def head(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def initialize(self, request, response):
        super(BareBaseRequestHandler, self).initialize(request, response)
        for arg in sorted(self.request.GET):
            logging.info("query %r = %r", arg, self.request.GET.getall(arg))

        self.display['indexing_bot'] = 'googlebot' in (self.request.user_agent or '').lower()

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
            logging.warning("Returning errors to the user: %s", self._errors)
            raise _ValidationError(self._errors)

    def handle_exception(self, e, debug):
        handled = False
        if isinstance(e, _ValidationError):
            handled = self.handle_error_response(self._errors)
        if not handled:
            raise
            # super(BareBaseRequestHandler, self).handle_exception(e, debug)

    def handle_error_response(self, errors):
        if self.request.method == 'POST':
            # call get response handler if we have post validation errors
            self.get()
            return True
        else:
            # let exception handling code operate normally
            return False

    def write_json_response(self, arg):
        self.response.out.write(json.dumps(arg))

    def render_template(self, name):
        jinja_template = self.jinja_env.get_template("%s.html" % name)
        rendered = jinja_template.render(**self.display)
        if 'clean' not in self.debug_list:
            rendered = htmlmin.minify(
                rendered,
                remove_comments=True,
                remove_empty_space=True,
                reduce_boolean_attributes=True,
            )
        self.response.out.write(rendered)

    def get_location_from_headers(self, city=True):
        iso3166_country = self.request.headers.get("X-AppEngine-Country")
        full_country = abbrev.countries_abbrev2full.get(iso3166_country, iso3166_country)

        location_components = []
        if city:
            location_components.append(self.request.headers.get("X-AppEngine-City"))
        if full_country in ['United States', 'Canada']:
            location_components.append(self.request.headers.get("X-AppEngine-Region"))
        if full_country != 'ZZ':
            location_components.append(full_country)
        location = ', '.join(x for x in location_components if x and x != '?')
        return location


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

    def __init__(self, *args, **kwargs):
        self.fb_uid = None
        self.user = None
        self.access_token = None
        super(BaseRequestHandler, self).__init__(*args, **kwargs)

    def get_long_lived_token_and_expires(self, request):
        response = facebook.get_user_from_cookie(request.cookies)
        return response['access_token'], response['access_token_expires']

    def set_login_cookie(self, fb_cookie_uid, access_token_md5=None):
        """Sets the user_login cookie that we use to track if the user is logged in.
        Normally this is our authoritative reference, and if any discrepancies occur with the FB cookie,
        we try to re-login as the FB cookie (which may or may not exist).

        However, if the access_token_md5 is set, then we stay logged in as the user regardless,
        which is a forcing-login function of sorts. This is used by the mobile apps,
        to send the user to a logged-in page.
        """
        user_login_cookie = {
            'uid': fb_cookie_uid,
        }
        if access_token_md5:
            user_login_cookie['access_token_md5'] = access_token_md5
        user_login_cookie['hash'] = generate_userlogin_hash(user_login_cookie)
        user_login_string = urllib.quote(json.dumps(user_login_cookie))
        logging.info("setting cookie response... to %s", user_login_string)
        self.response.set_cookie(self._get_login_cookie_name(), user_login_string, max_age=30*24*60*60, path='/', domain=self._get_login_cookie_domain())

    def _get_login_cookie_domain(self):
        domain = self.request.host.replace('www.', '.')
        if ':' in domain:
            domain = domain.split(':')[0]
        return domain

    def _get_login_cookie_name(self):
        return 'user_login_' + facebook.FACEBOOK_CONFIG['app_id']

    def get_login_cookie(self):
        return self.request.cookies.get(self._get_login_cookie_name(), self.request.cookies.get('user_login', ''))

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
        try:
            response = facebook.parse_signed_request_cookie(request.cookies)
        except Cookie.CookieError:
            logging.exception("Error processing cookie: %s")
            return
        fb_cookie_uid = None
        if response:
            fb_cookie_uid = response['user_id']
        logging.info("fb cookie id is %s", fb_cookie_uid)

        # Normally, our trusted source of login id is the FB cookie,
        # though we may override it below in the case of access_token_md5
        trusted_cookie_uid = fb_cookie_uid

        # Load our dancedeets logged-in user/state
        our_cookie_uid = None
        user_login_string = self.get_login_cookie()
        if user_login_string:
            user_login_cookie = json.loads(urllib.unquote(user_login_string))
            if validate_hashed_userlogin(user_login_cookie):
                our_cookie_uid = user_login_cookie['uid']
                # If we have a browser cookie that's verified via access_token_md5,
                # so let's trust it as authoritative here and ignore the fb cookie
                if not trusted_cookie_uid and user_login_cookie.get('access_token_md5'):
                    trusted_cookie_uid = our_cookie_uid

        if self.request.cookies.get('user_login', ''):
            self.response.set_cookie('user_login', '', max_age=0, path='/', domain=self._get_login_cookie_domain())

        # If the user has changed facebook users, let's automatically re-login at dancedeets
        if trusted_cookie_uid and trusted_cookie_uid != our_cookie_uid:
            self.set_login_cookie(trusted_cookie_uid)
            our_cookie_uid = trusted_cookie_uid

        # Don't force-logout the user if there is a our_cookie_uid but not a trusted_cookie_uid
        # The fb cookie probably expired after a couple hours, and we'd prefer to keep our users logged-in

        # Logged-out view, just return without setting anything up
        if not our_cookie_uid:
            return

        self.fb_uid = our_cookie_uid
        self.user = users.User.get_by_id(self.fb_uid)

        # If we have a user, grab the access token
        if self.user:
            if trusted_cookie_uid:
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
                    except TypeError:
                        logging.info("Could not access cookie ")
                    except facebook.AlreadyHasLongLivedToken:
                        logging.info("Already have long-lived token, FB wouldn't give us a new one, so no need to refresh anything.")
                    else:
                        logging.info("New access token from cookie: %s, expires %s", access_token, access_token_expires)
                        if access_token:
                            self.user = users.User.get_by_id(self.fb_uid)
                            self.user.fb_access_token = access_token
                            self.user.fb_access_token_expires = access_token_expires
                            self.user.expired_oauth_token = False
                            self.user.expired_oauth_token_reason = None
                            # this also sets to memcache
                            self.user.put()
                            logging.info("Stored the new access_token to the User db")
                        else:
                            logging.error("Got a cookie, but no access_token. Using the one from the existing user. Strange!")
                if 'web' not in self.user.clients:
                    self.user = users.User.get_by_id(self.fb_uid)
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
        elif trusted_cookie_uid:
            # if we don't have a user but do have a token, the user has granted us permissions, so let's construct the user now
            try:
                access_token, access_token_expires = self.get_long_lived_token_and_expires(request)
            except facebook.AlreadyHasLongLivedToken:
                logging.warning("Don't have user, just trusted_cookie_uid. And unable to get long lived token for the incoming request. Giving up and doing logged-out")
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
            # TODO(lambert): handle this MUUUCH better
            logging.info("Not a /login request and there is no user object, constructed one realllly-quick, and continuing on.")
            self.user = users.User.get_by_id(self.fb_uid)
            # Should not happen:
            if not self.user:
                logging.error("We still don't have a user!")
                self.fb_uid = None
                self.access_token = None
                self.user = None
                return
        else:
            # no user, no trusted_cookie_uid, but we have fb_uid from the user_login cookie
            logging.error("We have a user_login cookie, but no user, and no trusted_cookie_uid. Acting as logged-out")
            self.fb_uid = None
            self.access_token = None
            self.user = None
            return

        logging.info("Logged in uid %s with name %s and token %s", self.fb_uid, self.user.full_name, self.access_token)

        # Track last-logged-in state
        hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        if not getattr(self.user, 'last_login_time', None) or self.user.last_login_time < hour_ago:
            # Do this in a separate request so we don't increase latency on this call
            deferred.defer(update_last_login_time, self.user.fb_uid, datetime.datetime.now(), _queue='slow-queue')
            backgrounder.load_users([self.fb_uid], allow_cache=False)

    def handle_alternate_login(self, request):
        # If the mobile app sent the user to a /....?uid=XX&access_token_md5=YY URL,
        # then let's verify the parameters, and log the user in as that user
        if request.get('uid'):
            if request.get('access_token'):
                fbl = fb_api.FBLookup(request.get('uid'), request.get('access_token'))
                fb_user = fbl.get(fb_api.LookupUser, 'me')
                logging.info("Requested /me with given access_token, got %s", fb_user)

                if fb_user['profile']['id'] == request.get('uid'):
                    user = users.User.get_by_id(request.get('uid'))
                    access_token_md5 = hashlib.md5(user.fb_access_token).hexdigest()
                    self.set_login_cookie(request.get('uid'), access_token_md5=access_token_md5)
            if request.get('access_token_md5'):
                user = users.User.get_by_id(request.get('uid'))
                if request.get('access_token_md5') == hashlib.md5(user.fb_access_token).hexdigest():
                    # Authenticated! Now save cookie so subsequent requests can trust that this user is authenticated.
                    # The subsequent request will see a valid user_login param (though without an fb_cookie_uid)
                    self.set_login_cookie(request.get('uid'), access_token_md5=self.request.get('access_token_md5'))
            # But regardless of whether the token was correct, let's redirect and get rid of these url params.
            current_url_args = {}
            for arg in sorted(self.request.GET):
                if arg in ['uid', 'access_token', 'access_token_md5']:
                    continue
                current_url_args[arg] = [x.encode('utf-8') for x in self.request.GET.getall(arg)]
            final_url = self.request.path + '?' + urllib.urlencode(current_url_args, doseq=True)
            # Make sure we abort=True, since otherwise the caller will keep on running the initialize() code.
            return final_url
        else:
            return False

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

        redirect_url = self.handle_alternate_login(request)
        if redirect_url:
            self.run_handler = False
            self.redirect(redirect_url)
            return

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
            self.jinja_env.filters['date_only_human_format'] = self.user.date_only_human_format
            self.jinja_env.filters['date_human_format'] = self.user.date_human_format
            self.jinja_env.filters['time_human_format'] = self.user.time_human_format
            self.jinja_env.globals['duration_human_format'] = self.user.duration_human_format
            self.display['messages'] = self.user.get_and_purge_messages()
        else:
            self.jinja_env.filters['date_only_human_format'] = dates.date_only_human_format
            self.jinja_env.filters['date_human_format'] = dates.date_human_format
            self.jinja_env.filters['time_human_format'] = dates.time_human_format
            self.jinja_env.globals['duration_human_format'] = dates.duration_human_format
            self.display['login_url'] = login_url
        self.jinja_env.filters['datetime_format'] = dates.datetime_format

        self.jinja_env.globals['fb_event_url'] = urls.fb_event_url
        self.jinja_env.globals['raw_fb_event_url'] = urls.raw_fb_event_url
        self.jinja_env.globals['dd_admin_event_url'] = urls.dd_admin_event_url
        self.jinja_env.globals['dd_admin_source_url'] = urls.dd_admin_source_url

        self.display['request'] = request
        self.display['app_id'] = facebook.FACEBOOK_CONFIG['app_id']
        self.display['prod_mode'] = self.request.app.prod_mode

        self.display['base_hostname'] = 'dancedeets.com' if self.request.app.prod_mode else 'dev.dancedeets.com'
        self.display['full_hostname'] = 'www.dancedeets.com' if self.request.app.prod_mode else app_identity.get_default_version_hostname()

        self.display['keyword_tokens'] = [{'value': x.public_name} for x in styles.STYLES]
        fb_permissions = 'rsvp_event,email,user_events'
        if self.request.get('all_access'):
            fb_permissions += ',read_friendlists,manage_pages'
        self.display['fb_permissions'] = fb_permissions

        already_used_mobile = self.user and ('android' in self.user.clients or 'ios' in self.user.clients)
        mobile_platform = mobile.get_mobile_platform(self.request.user_agent)
        show_mobile_promo = not mobile_platform and not already_used_mobile
        self.display['show_mobile_promo'] = show_mobile_promo
        self.display['mobile_platform'] = mobile_platform
        if mobile_platform == mobile.MOBILE_ANDROID:
            self.display['mobile_app_url'] = mobile.ANDROID_URL
        elif mobile_platform == mobile.MOBILE_IOS:
            self.display['mobile_app_url'] = mobile.IOS_URL
        self.display['mobile'] = mobile
        self.display['mobile_show_smartbanner'] = True

        self.display['ip_location'] = self.get_location_from_headers()

        self.display['styles'] = styles.STYLES
        self.display['us_cities'] = [
            'New York, NY',
            'Los Angeles, CA',
            'San Francisco, CA',
            '',
            'Anaheim, CA',
            'Boston, MA',
            'Chicago, IL',
            'Detroit, MI',
            'Las Vegas, CA',
            'Montreal, Canada',
            'Ottowa, Canada',
            'Philadelphia, PA',
            'Phoenix, AZ',
            'Portland, OR',
            'Sacramento, CA',
            'San Diego, CA',
            'Seattle, WA',
            'Toronto, Canada',
            'Vancouver, Canada',
            'Washington, DC',
        ]
        self.display['eu_cities'] = [
            'Amsterdam, Netherlands',
            'Barcelona, Spain',
            'Berlin, Germany',
            'Bratislava, Slovakia',
            'Brno, Czech Republic',
            'Brussels, Belgium',
            'Copenhagen, Denmark',
            'Frankfurt, Germany',
            'Geneva, Switzerland',
            'Helsinki, Finland',
            'London, UK',
            'Lyon, France',
            'Manchester, United Kingdom',
            'Marseille, France',
            'Milan, Italy',
            'Oslo, Norway',
            'Paris, France',
            'Rome, Italy',
            'Stockholm, Sweden',
            'Vienna, Austria',
            'Warsaw, Poland',
            'Zurich, Switzerland',

        ]
        self.display['other'] = [
            'Argentina',
            'Australia',
            'Brasil: Minas Gerais',
            'Colombia',
            'Hong Kong',
            'India',
            'Japan: Osaka',
            'Japan: Tokyo',
            'Malaysia',
            'New Zealand',
            'Peru',
            'Philippines',
            'Singapore',
            'Taiwan',
        ]

        self.display['deb'] = self.request.get('deb')
        self.display['debug_list'] = self.debug_list
        self.display['user'] = self.user

        webview = bool(request.get('webview'))
        self.display['webview'] = webview
        if webview:
            self.display['class_base_template'] = '_base_webview.html'
        else:
            self.display['class_base_template'] = '_base.html'

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


def update_last_login_time(user_id, login_time):
    def _update_last_login_time():
        user = users.User.get_by_id(user_id)
        user.last_login_time = login_time
        if user.login_count:
            user.login_count += 1
        else:
            # once for this one, once for initial creation
            user.login_count = 2
        # in read-only, keep trying until we succeed
        user.put()
    db.run_in_transaction(_update_last_login_time)


class BaseTaskRequestHandler(webapp2.RequestHandler):
    pass


class BaseTaskFacebookRequestHandler(BaseTaskRequestHandler):
    def requires_login(self):
        return False

    def initialize(self, request, response):
        super(BaseTaskFacebookRequestHandler, self).initialize(request, response)

        if self.request.get('user_id') == 'dummy':
            self.fb_uid = None
            self.user = None
            self.access_token = None
        else:
            self.fb_uid = self.request.get('user_id')
            if not self.fb_uid:
                self.abort(400, 'Need valid user_id argument')
                return
            self.user = users.User.get_by_id(self.fb_uid)
            if self.user:
                if not self.user.fb_access_token:
                    logging.error("Can't execute background task for user %s without access_token", self.fb_uid)
                self.access_token = self.user.fb_access_token
            else:
                self.access_token = None
        self.allow_cache = bool(int(self.request.get('allow_cache', 1)))
        force_updated = bool(int(self.request.get('force_updated', 0)))
        self.fbl = fb_api.FBLookup(self.fb_uid, self.access_token)
        self.fbl.allow_cache = self.allow_cache
        self.fbl.force_updated = force_updated

        # Refresh our potential event cache every N days (since they may have updated with better keywords, as often happens)
        expiry_days = int(self.request.get('expiry_days', 0)) or None
        if expiry_days:
            self.fbl.db.oldest_allowed = datetime.datetime.now() - datetime.timedelta(days=expiry_days)
