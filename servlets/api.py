import datetime
import json
import logging
import urllib

from google.appengine.api import taskqueue

import app
import base_servlet
import event_types
import fb_api
from event_scraper import add_entities
from events import add_events
from events import eventdata
from loc import formatting
from loc import gmaps_api
from loc import math
from search import onebox
from search import search
from search import search_base
from users import user_creation
from users import users

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATETIME_FORMAT_TZ = "%Y-%m-%dT%H:%M:%S%z"

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
                self.fbl = fb_api.FBLookup(None, self.json_body.get('access_token'))
                self.fbl.make_passthrough()
                self.fb_user = self.fbl.get(fb_api.LookupUser, 'me')
                self.fb_uid = self.fb_user['profile']['id']
                logging.info("Access token for user ID %s", self.fb_uid)
            elif self.requires_auth:
                self.add_error("Needs access_token parameter")

    def dispatch(self):
        try:
            major_version, minor_version = self.request.route_args[0:2]
            self.request.route_args = self.request.route_args[2:]
            self.version = (int(major_version), int(minor_version))
            self._initialize(self.request)
            super(ApiHandler, self).dispatch()
        except Exception as e:
            logging.exception("API failure")
            result = e.args[0]
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

@apiroute('/search')
class SearchHandler(ApiHandler):

    def _get_title(self, location, keywords):
        if location:
            if keywords:
                return "Events near %s containing %s" % (location, keywords)
            else:
                return "Events near %s" % location
        else:
            if keywords:
                return "Events containing %s" % keywords
            else:
                return "Events"

    def get(self):
        data = {
            'location': self.request.get('location'),
            'keywords': self.request.get('keywords'),
        }
        # If it's 1.0 clients, or web clients, then grab all data
        if self.version == (1, 0):
            time_period = search_base.TIME_UPCOMING
        else:
            time_period = self.request.get('time_period')
        data['time_period'] = time_period
        form = search_base.SearchForm(data=data)

        if not form.validate():
            for field, errors in form.errors.items():
                for error in errors:
                    self.add_error(u"%s error: %s" % (
                        getattr(form, field).label.text,
                        error
                    ))

        if not form.location.data:
            city_name = None
            southwest = None
            northeast = None
            if not form.keywords.data:
                if self.version == (1, 0):
                    self.write_json_success({'results': []})
                    return
                else:
                    self.add_error('Please enter a location or keywords')
        else:
            geocode = gmaps_api.get_geocode(address=form.location.data)
            if geocode:
                southwest, northeast = math.expand_bounds(geocode.latlng_bounds(), form.distance_in_km())
                city_name = formatting.format_geocode(geocode)
                # This will fail on a bad location, so let's verify the location is geocodable above first.
            else:
                if self.version == (1, 0):
                    self.write_json_success({'results': []})
                    return
                else:
                    self.add_error('Could not geocode location')

        self.errors_are_fatal()

        search_results = []
        distances = [50, 100, 170, 300]
        distance_index = 0
        while not search_results:
            form.distance.data = distances[distance_index]
            form.distance_units.data = 'miles'
            search_query = form.build_query()
            searcher = search.Search(search_query)
            # TODO(lambert): Increase the size limit when our clients can handle it. And improve our result sorting to return the 'best' results.
            searcher.limit = 500
            search_results = searcher.get_search_results(full_event=True)

            # Increase our search distance in the hopes of finding something
            distance_index += 1
            if distance_index == len(distances):
                # If we searched the world, then break
                break

        logging.info("Found %r events within %s %s of %s", form.keywords.data, form.distance.data, form.distance_units.data, form.location.data)
        onebox_links = onebox.get_links_for_query(search_query)

        json_results = []
        for result in search_results:
            try:
                json_result = canonicalize_event_data(result.db_event, result.event_keywords)
                json_results.append(json_result)
            except Exception as e:
                logging.exception("Error processing event %s: %s" % (result.event_id, e))

        title = self._get_title(city_name, form.keywords.data)
        json_response = {
            'results': json_results,
            'onebox_links': onebox_links,
            'title': title,
            'location': city_name,
        }
        if southwest and northeast:
            json_response['location_box'] = {
                'southwest': {
                    'latitude': southwest[0],
                    'longitude': southwest[1],
                },
                'northeast': {
                    'latitude': northeast[0],
                    'longitude': northeast[1],
                },
            }
        self.write_json_success(json_response)


class LookupDebugToken(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('token', cls.url('debug_token?input_token=%s' % object_id)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fb_api.USERLESS_UID, object_id, 'OBJ_DEBUG_TOKEN')


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
        self.errors_are_fatal() # Assert that our access_token is set

        # Fetch the access_token_expires value from Facebook, instead of demanding it via the API
        app_fbl = fb_api.FBLookup(None, fb_api.facebook.FACEBOOK_CONFIG['app_access_token'])
        app_fbl.allow_cache = False
        debug_info = app_fbl.get(LookupDebugToken, access_token)
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
                    user.login_count = 2 # once for this one, once for initial creation
            user.last_login_time = datetime.datetime.now()

            update_user(self, user, self.json_body)

            user.put() # this also sets to memcache
        else:
            client = self.json_body.get('client')
            location = self.json_body.get('location')
            user_creation.create_user_with_fbuser(self.fb_uid, self.fb_user, access_token, access_token_expires, location, client=client)
        self.write_json_success()


@apiroute('/user')
class UserUpdateHandler(ApiHandler):
    requires_auth = True

    def post(self):
        self.errors_are_fatal() # Assert that our access_token is set

        user = users.User.get_by_id(self.fb_uid)
        if not user:
            raise RetryException("User does not yet exist, cannot modify it yet.")

        update_user(self, user, self.json_body)

        user.put() # this also sets to memcache
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


def canonicalize_event_data(db_event, event_keywords):
    event_api = {}
    event_api['id'] = db_event.id
    event_api['name'] = db_event.name
    event_api['start_time'] = db_event.start_time_with_tz.strftime(DATETIME_FORMAT_TZ)
    event_api['description'] = db_event.description
    # end time can be optional, especially on single-day events that are whole-day events
    if db_event.end_time_with_tz:
        event_api['end_time'] = db_event.end_time_with_tz.strftime(DATETIME_FORMAT_TZ)
    else:
        event_api['end_time'] = None
    event_api['source'] = {
        'name': db_event.source_name,
        'url': db_event.source_url,
    }

    # cover images
    cover_images = db_event.cover_images
    if cover_images:
        event_api['cover'] = {
            'cover_id': 'dummy', # Android (v1.1) expects this value, even though it does nothing with it.
            'images': sorted(cover_images, key=lambda x: -x['height']),
        }
    else:
        event_api['cover'] = None
    event_api['picture'] = db_event.image_url

    # location data
    if db_event.location_name:
        venue_location_name = db_event.location_name
    # We could do something like this...
    # elif db_event and db_event.actual_city_name:
    #    venue_location_name = db_event.actual_city_name
    # ...but really, this would return the overridden/remapped address name, which would likely just be a "City" anyway.
    # A city isn't particularly useful for our clients trying to display the event on a map.
    else:
        # In these very rare cases (where we've manually set the location on a location-less event), return ''
        # TODO: We'd ideally like to return None, but unfortunately Android expects this to be non-null in 1.0.3 and earlier.
        venue_location_name = ""
    venue = db_event.venue
    if 'name' in venue and venue['name'] != venue_location_name:
        logging.error("For event %s, venue name %r is different from location name %r", db_event.fb_event_id, venue['name'], venue_location_name)
    venue_id = None
    if 'id' in venue:
        venue_id = venue['id']
    address = None
    if 'country' in venue:
        address = {}
        for key in ['street', 'city', 'state', 'zip', 'country']:
            if key in venue:
                address[key] = venue.get(key)
    geocode = None
    if db_event.longitude and db_event.latitude:
        geocode = {
            'longitude': db_event.longitude,
            'latitude': db_event.latitude,
        }
    # I have seen:
    # - no venue subfields at all (ie, we manually specify the address/location in the event or remapping), which will be returned as "" here (see above comment)
    # - name only (possibly remapped?)
    # - name and id and geocode
    # - name and address and id and geocode
    # - name and address (everything except zip) and id and geocode
    # - so now address can be any subset of those fields that the venue author filled out...but will specify country, at least
    # ...are there more variations? write a mapreduce on recent events to check?
    event_api['venue'] = {
        'name': venue_location_name,
        'id': venue_id,
        'address': address,
        'geocode': geocode,
    }
    # people data
    event_api['admins'] = db_event.admins

    annotations = {}
    if db_event and db_event.creation_time:
        annotations['creation'] = {
            'time': db_event.creation_time.strftime(DATETIME_FORMAT),
            'method': db_event.creating_method,
            'creator': db_event.creating_fb_uid,
        }
    # We may have keywords from the search result that called us
    if event_keywords:
        annotations['dance_keywords'] = event_keywords
        annotations['categories'] = event_keywords
    # or from the db_event associated with this
    elif db_event:
        annotations['dance_keywords'] = db_event.event_keywords
    # or possibly none at all, if we only received a fb_event..
    else:
        pass
    if db_event: # TODO: When is this not true?
        annotations['categories'] = event_types.humanize_categories(db_event.auto_categories)

    event_api['annotations'] = annotations
    # maybe handle: 'ticket_uri', 'timezone', 'updated_time', 'is_date_only'
    # rsvp_fields = ['attending_count', 'declined_count', 'maybe_count', 'noreply_count', 'invited_count']
    if db_event.attending_count or db_event.maybe_count:
        event_api['rsvp'] = {
            'attending_count': db_event.attending_count or 0,
            'maybe_count': db_event.maybe_count or 0,
        }
    else:
        event_api['rsvp'] = None

    return event_api


@apiroute('/events_add')
class AddHandler(ApiHandler):
    requires_auth = True

    def get(self):
        events = add_events.get_decorated_user_events(self.fbl)
        self.write_json_success({'events': events})

    def post(self):
        event_id = self.json_body.get('event_id')
        if event_id:
            self.add_error('Need to pass event_id argument')
        self.errors_are_fatal()
        fb_event = self.fbl.get(fb_api.LookupEvent, event_id, allow_cache=False)
        add_entities.add_update_event(fb_event, self.fbl, creating_uid=self.fbl.fb_uid, creating_method=eventdata.CM_USER)
        self.write_json_success()


@apiroute(r'/events/%s' % eventdata.EVENT_ID_REGEX)
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

        json_data = canonicalize_event_data(db_event, None)

        # Ten minute expiry on data we return
        self.response.headers['Cache-Control'] = 'max-age=%s' % (60 * 10)
        self.write_json_success(json_data)
