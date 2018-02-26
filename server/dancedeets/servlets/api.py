import datetime
import feedparser
import json
import logging
import time
import urllib

from google.appengine.api import memcache
from googleapiclient.discovery import build

from dancedeets import app
from dancedeets import base_servlet
from dancedeets.event_scraper import add_entities
from dancedeets.events import add_events
from dancedeets.events import eventdata
from dancedeets import fb_api
from dancedeets import keys
from dancedeets.search import search
from dancedeets.search import search_base
from dancedeets.users import user_creation
from dancedeets.users import users
from dancedeets.util import ips
from dancedeets.util import taskqueue
from dancedeets.util import urls
from dancedeets.logic import api_format

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATETIME_FORMAT_TZ = "%Y-%m-%dT%H:%M:%S%z"


def get_user_id_for_token(access_token):
    key = 'AccessTokenToID: %s' % access_token
    user_id = memcache.get(key)
    if not user_id:
        result = fb_api.FBAPI(access_token).get('me', {'fields': 'id'})
        user_id = result['id']
        memcache.set(key, user_id)
    return user_id


class ApiHandler(base_servlet.BareBaseRequestHandler):
    requires_auth = False
    supports_auth = False

    def requires_login(self):
        return False

    def write_json_error(self, error_result):
        return self._write_json_data(error_result)

    def write_json_success(self, results=None):
        if results is None:
            results = {'success': True}
        return self._write_json_data(results)

    def _write_json_data(self, json_data):
        callback = self.request.get('callback')
        if callback:
            self.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
        else:
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'

        if callback:
            self.response.out.write('%s(' % callback)
        self.response.out.write(json.dumps(json_data))
        if callback:
            self.response.out.write(')')

    def _initialize(self, request):
        self.response.headers.add_header('Access-Control-Allow-Headers', 'Content-Type')

        # We use _initialize instead of webapp2's initialize, so that exceptions can be caught easily
        self.fbl = fb_api.FBLookup(None, None)

        if self.request.body:
            logging.info("Request body: %r", self.request.body)
            escaped_body = urllib.unquote_plus(self.request.body.strip('='))
            self.json_body = json.loads(escaped_body)
            logging.info("json_request: %r", self.json_body)
        else:
            self.json_body = None

        if self.requires_auth or self.supports_auth:
            if self.json_body.get('access_token'):
                access_token = self.json_body.get('access_token')
                self.fb_uid = get_user_id_for_token(access_token)
                self.fbl = fb_api.FBLookup(self.fb_uid, access_token)
                logging.info("Access token for user ID %s", self.fb_uid)
            elif self.requires_auth:
                self.add_error("Needs access_token parameter")

    def handle_error_response(self, errors):
        # We don't handle errors, but instead just pass them onto the client in our json responses
        return False

    def dispatch(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        try:
            major_version, minor_version = self.request.route_args[0:2]
            self.request.route_args = self.request.route_args[2:]
            self.version = (int(major_version), int(minor_version))
            self._initialize(self.request)
            super(ApiHandler, self).dispatch()
        except Exception as e:
            logging.exception("API failure")
            result = e.args and e.args[0] or e
            # If it's a string or a regular object
            if not hasattr(result, '__iter__'):
                result = [result]
            self.write_json_error({'success': False, 'errors': [unicode(x) for x in result]})


def apiroute(path, *args, **kwargs):
    return app.route('/api/v(\d+)\.(\d+)' + path, *args, **kwargs)


class RetryException(Exception):
    pass


def retryable(func):
    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self = args[0]
            logging.exception("API retry failure")
            url = self.request.path
            body = self.request.body
            logging.error(e)
            logging.error("Retrying URL %s", url)
            logging.error("With Payload %r", body)
            taskqueue.add(method='POST', url=url, payload=body, countdown=60 * 60)
            raise

    return wrapped_func


@apiroute('/people')
class PeopleHandler(ApiHandler):
    def get(self):
        data = {
            'location': self.request.get('location'),
            'locale': self.request.get('locale'),
        }
        form = search_base.SearchForm(data=data)

        if not form.validate():
            for field, errors in form.errors.items():
                for error in errors:
                    self.add_error(u"%s error: %s" % (getattr(form, field).label.text, error))

        if not form.location.data:
            self.add_error('Need location')
        else:
            try:
                geocode, distance = search_base.get_geocode_with_distance(form)
            except:
                self.add_error('Could not geocode location')
        self.errors_are_fatal()

        groupings = api_format.people_groupings(geocode, distance, skip_people=False)
        self.write_json_success({'people': groupings})

    post = get


@apiroute('/search')
class SearchHandler(ApiHandler):
    def _build_search_form_data(self):
        data = {
            'location': self.request.get('location'),
            'keywords': self.request.get('keywords'),
            'skip_people': self.request.get('skip_people'),
        }
        for key in ['locale', 'deb']:
            if self.request.get(key):
                data[key] = self.request.get(key)
        for key in ['min_worth']:
            if self.request.get(key):
                data[key] = int(self.request.get(key))
        for key in ['start', 'end']:
            if self.request.get(key):
                dt = datetime.datetime.strptime(self.request.get(key), '%Y-%m-%d')
                if dt:
                    data[key] = dt.date()
        return data

    def get(self):
        data = self._build_search_form_data()
        form = search_base.SearchForm(data=data)

        if not form.validate():
            for field, errors in form.errors.items():
                for error in errors:
                    self.add_error(u"%s error: %s" % (getattr(form, field).label.text, error))

        geocode = None
        distance = None
        if form.location.data:
            try:
                geocode, distance = search_base.get_geocode_with_distance(form)
            except:
                self.add_error('Could not geocode location')

        if self.has_errors():
            if self.version == (1, 0):
                self.write_json_success({'results': []})
                return
            else:
                self.errors_are_fatal()

        search_results = []
        form.distance.data = 50
        form.distance_units.data = 'km'
        search_query = form.build_query()
        searcher = search.Search(search_query, deb=form.deb.data)
        need_full_event = self.version < (2, 0)
        # TODO(lambert): Increase the size limit when our clients can handle it. And improve our result sorting to return the 'best' results.
        searcher.limit = 500 if need_full_event else 1000
        search_results = searcher.get_search_results(full_event=need_full_event)

        logging.info(
            "Found %s keyword=%r events within %s %s of %s", len(search_results), form.keywords.data, form.distance.data,
            form.distance_units.data, form.location.data
        )

        # Keep in sync with mobile react code? And search_servlets
        skip_people = len(search_results) >= 10 or form.skip_people.data
        json_response = api_format.build_search_results_api(
            form, search_query, search_results, self.version, need_full_event, geocode, distance, skip_people=skip_people
        )
        if self.request.get('client') == 'react-android' and self.version <= (1, 3):
            json_response['featured'] = []
        self.write_json_success(json_response)

    post = get


def update_user(servlet, user, json_body):
    location = json_body.get('location')
    if location:
        # If we had a geocode failure, or had a geocode bug, or we did a geocode bug and only got a country
        user.location = location
    else:
        # Use the IP address headers if we've got nothing better
        if not user.location:
            user.location = servlet.get_location_from_headers()

    if not getattr(user, 'json_data', None):
        user.json_data = {}
    android_token = json_body.get('android_device_token')
    if android_token:
        tokens = user.device_tokens('android')
        if android_token not in tokens:
            tokens.append(android_token)
    ios_token = json_body.get('ios_device_token')
    if ios_token:
        tokens = user.device_tokens('ios')
        if android_token not in tokens:
            tokens.append(android_token)


# Released a version of iOS that requested from /api/v1.1auth, so let's handle that here for awhile
@apiroute('/auth')
class AuthHandler(ApiHandler):
    requires_auth = True

    @retryable
    def post(self):
        access_token = self.json_body.get('access_token')
        if not access_token:
            self.write_json_error({'success': False, 'errors': ['No access token']})
            logging.error("Received empty access_token from client. Payload was: %s", self.json_body)
            return
        self.errors_are_fatal()  # Assert that our access_token is set

        # Fetch the access_token_expires value from Facebook, instead of demanding it via the API
        debug_info = fb_api.lookup_debug_tokens([access_token])[0]
        if debug_info['empty']:
            logging.error('Error: %s', debug_info['empty'])
            raise Exception(debug_info['empty'])
        access_token_expires_timestamp = debug_info['token']['data'].get('expires_at')
        if access_token_expires_timestamp:
            access_token_expires = datetime.datetime.fromtimestamp(access_token_expires_timestamp)
        else:
            access_token_expires = None

        logging.info("Auth tokens is %s", access_token)

        user = users.User.get_by_id(self.fb_uid)
        if user:
            logging.info("User exists, updating user with new fb access token data")
            user.fb_access_token = access_token
            user.fb_access_token_expires = access_token_expires
            user.expired_oauth_token = False
            user.expired_oauth_token_reason = ""

            client = self.json_body.get('client')
            if client and client not in user.clients:
                user.clients.append(client)

            # Track usage stats
            if user.last_login_time < datetime.datetime.now() - datetime.timedelta(hours=1):
                if user.login_count:
                    user.login_count += 1
                else:
                    user.login_count = 2  # once for this one, once for initial creation
            user.last_login_time = datetime.datetime.now()

            update_user(self, user, self.json_body)

            user.put()  # this also sets to memcache
        else:
            client = self.json_body.get('client')
            location = self.json_body.get('location')
            fb_user = self.fbl.get(fb_api.LookupUser, 'me')
            ip = ips.get_remote_ip(self.request)
            user_creation.create_user_with_fbuser(self.fb_uid, fb_user, access_token, access_token_expires, location, ip, client=client)
        self.write_json_success()


@apiroute('/user')
class UserUpdateHandler(ApiHandler):
    requires_auth = True

    def post(self):
        self.errors_are_fatal()  # Assert that our access_token is set

        user = users.User.get_by_id(self.fb_uid)
        if not user:
            raise RetryException("User does not yet exist, cannot modify it yet.")

        update_user(self, user, self.json_body)

        user.put()  # this also sets to memcache
        self.write_json_success()


class SettingsHandler(ApiHandler):
    requires_auth = True

    def get(self):
        user = users.User.get_by_id(self.fb_uid)
        json_data = {
            'location': user.location,
            'distance': user.distance,
            'distance_units': user.distance_units,
            'send_email': user.send_email,
        }
        self.write_json_success(json_data)

    def post(self):
        user = users.User.get_by_id(self.fb_uid)
        json_request = json.loads(self.request.body)
        if json_request.get('location'):
            user.location = json_request.get('location')
        if json_request.get('distance'):
            user.distance = json_request.get('distance')
        if json_request.get('distance_units'):
            user.distance_units = json_request.get('distance_units')
        if json_request.get('send_email'):
            user.send_email = json_request.get('send_email')
        user.put()

        self.write_json_success()


@apiroute('/user/info')
class UserInfoHandler(ApiHandler):
    requires_auth = True

    def get(self):
        self.errors_are_fatal()

        user = users.User.get_by_id(self.fb_uid)
        if not user:
            results = {
                'location': '',
                'creation_time': datetime.datetime.now().strftime(DATETIME_FORMAT_TZ),
                'num_auto_added_events': 0,
                'num_auto_added_own_events': 0,
                'num_hand_added_events': 0,
                'num_hand_added_own_events': 0,
            }
        else:
            results = {
                'location': user.location,
                'creation_time': user.creation_time.strftime(DATETIME_FORMAT_TZ),
                'num_auto_added_events': user.num_auto_added_events,
                'num_auto_added_own_events': user.num_auto_added_own_events,
                'num_hand_added_events': user.num_hand_added_events,
                'num_hand_added_own_events': user.num_hand_added_own_events,
            }
        self.write_json_success(results)

    post = get


@apiroute('/events_translate')
class EventTranslateHandler(ApiHandler):
    requires_auth = True

    def post(self):
        if self.json_body:
            event_id = self.json_body.get('event_id')
            language = self.json_body.get('language') or self.json_body.get('locale')
            if not event_id:
                self.add_error('Need to pass event_id argument')
            if not language:
                self.add_error('Need to pass language/locale argument')
        else:
            self.add_error('Need to pass a post body of json params')
        # Remap our traditional/simplified chinese languages
        if language == 'zh':
            language = 'zh-TW'
        elif language == 'zh-Hant':
            language = 'zh-TW'
        elif language == 'zh-Hans':
            language = 'zh-CN'
        self.errors_are_fatal()
        db_event = eventdata.DBEvent.get_by_id(event_id)
        service = build('translate', 'v2', developerKey=keys.get('google_server_key'))
        result = service.translations().list(target=language, format='text', q=[db_event.name or '', db_event.description or '']).execute()
        translations = [x['translatedText'] for x in result['translations']]
        self.write_json_success({'name': translations[0], 'description': translations[1]})

    get = post


@apiroute('/events_list_to_add')
class ListAddHandler(ApiHandler):
    requires_auth = True

    def post(self):
        events = add_events.get_decorated_user_events(self.fbl)
        self.write_json_success({'events': events})


@apiroute('/events_add')
class EventAddHandler(ApiHandler):
    requires_auth = True

    def post(self):
        event_id = self.json_body.get('event_id')
        if not event_id:
            self.add_error('Need to pass event_id argument')
        self.errors_are_fatal()
        fb_event = self.fbl.get(fb_api.LookupEvent, event_id, allow_cache=False)
        add_entities.add_update_fb_event(fb_event, self.fbl, creating_uid=self.fbl.fb_uid, creating_method=eventdata.CM_USER)
        self.write_json_success()


@apiroute(r'/events/%s' % urls.EVENT_ID_REGEX)
class EventHandler(ApiHandler):
    def get(self):
        path_bits = self.request.path.split('/events/')
        if len(path_bits) != 2:
            self.add_error('Path is malformed: %s' % self.request.path)
            self.response.out.write('Need an event_id.')
            return
        else:
            event_id = urllib.unquote_plus(path_bits[1].strip('/'))
            db_event = eventdata.DBEvent.get_by_id(event_id)
            if not db_event:
                self.add_error('No event found')
            elif not db_event.has_content():
                self.add_error('This event was empty: %s.' % db_event.empty_reason)

        self.errors_are_fatal()
        # '?locale=' + self.request.get('locale')
        # get venue address and stuffs
        # pass in as rewritten db_event for computing json_data

        if db_event.is_fb_event:
            fb_event_wall = self.fbl.get(fb_api.LookupEventWall, event_id)
        else:
            fb_event_wall = None
        json_data = api_format.canonicalize_event_data(db_event, self.version, event_wall=fb_event_wall)

        # Ten minute expiry on data we return
        self.response.headers['Cache-Control'] = 'public, max-age=%s' % (10 * 60)
        self.write_json_success(json_data)

    post = get


class DateHandlingJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, time.struct_time):
            return time.strftime(DATETIME_FORMAT, o)
        else:
            return json.JSONEncoder.default(self, o)


@apiroute(r'/feed')
class FeedHandler(ApiHandler):
    def get(self):
        if self.json_body:
            url = self.json_body.get('url')
        else:
            url = self.request.get('url')
        feed = feedparser.parse(url)
        json_string = json.dumps(feed, cls=DateHandlingJSONEncoder)
        json_data = json.loads(json_string)
        self.write_json_success(json_data)

    post = get
