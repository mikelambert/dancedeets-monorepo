import datetime
import feedparser
import json
import logging
from slugify import slugify
import time
import urllib

from google.appengine.api import memcache
from googleapiclient.discovery import build

import app
import base_servlet
import event_types
from event_scraper import add_entities
from events import add_events
from events import eventdata
from events import featured
import fb_api
import keys
from loc import address
from loc import gmaps_api
from loc import math
from event_attendees import popular_people
from rankings import cities
from search import onebox
from search import search
from search import search_base
from users import user_creation
from users import users
from util import ips
from util import language
from util import taskqueue
from util import urls

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
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


def people_groupings(geocode, distance, skip_people):
    groupings = None
    if skip_people or not geocode:
        groupings = {}
    else:
        center_latlng, southwest, northeast = search_base.get_center_and_bounds(geocode, distance)
        if not center_latlng:
            # keyword-only search, no location to give promoters for
            logging.info('No center latlng, skipping person groupings')
        else:
            distance_km = math.get_inner_box_radius_km(southwest, northeast)
            if distance_km > 1000:
                logging.info('Search area >1000km, skipping person groupings')
                # Too big a search area, not worth showing promoters or dancers
            else:
                # TODO: Replace with a call to get_attendees_within (that also gets ADMIN people)
                southwest_baseline, northeast_baseline = math.expand_bounds((center_latlng, center_latlng), cities.NEARBY_DISTANCE_KM)
                distance_km_baseline = math.get_inner_box_radius_km(southwest_baseline, northeast_baseline)
                if distance_km < distance_km_baseline:
                    southwest = southwest_baseline
                    northeast = northeast_baseline
                logging.info('Searching for cities within %s', (southwest, northeast))
                included_cities = cities.get_nearby_cities((southwest, northeast), only_populated=True)
                biggest_cities = sorted(included_cities, key=lambda x: -x.population)[:10]
                city_names = [city.display_name() for city in biggest_cities]
                logging.info('City names: %s', city_names)
                if city_names:
                    try:
                        people_rankings = popular_people.get_people_rankings_for_city_names(city_names)
                        groupings = popular_people.combine_rankings(people_rankings, max_people=10)
                    except:
                        logging.exception('Error creating combined people rankings')
                    new_groupings = {
                        'ADMIN': {},
                        'ATTENDEE': {},
                    }
                    # These lists can get huge now...make sure we trim them down for what clients need!
                    for person_type, styles in groupings.iteritems():
                        for style in event_types.STYLES + ['']:
                            index_style_name = style.index_name if style else ''
                            public_style_name = style.public_name if style else ''
                            good_style = None
                            for style in styles:
                                style_name, city = style.split(': ', 2)
                                if popular_people.is_summed_area(city) and style_name == index_style_name:
                                    good_style = style
                            if good_style:
                                new_groupings[person_type][public_style_name] = styles[good_style][:10]
                    groupings = new_groupings

                    logging.info('Person Groupings:\n%s', '\n'.join('%s: %s' % kv for kv in groupings.iteritems()))
    return groupings


def build_search_results_api(form, search_query, search_results, version, need_full_event, geocode, distance, skip_people=False):
    if geocode:
        center_latlng, southwest, northeast = search_base.get_center_and_bounds(geocode, distance)
    else:
        center_latlng = None
        southwest = None
        northeast = None

    onebox_links = []
    if search_query:
        onebox_links = onebox.get_links_for_query(search_query)

    json_results = []
    for result in search_results:
        try:
            if need_full_event:
                json_result = canonicalize_event_data(result.db_event, result.event_keywords, version)
            else:
                json_result = canonicalize_search_event_data(result, version)
            json_results.append(json_result)
        except Exception as e:
            logging.exception("Error processing event %s: %s" % (result.event_id, e))

    real_featured_infos = []
    try:
        featured_infos = featured.get_featured_events_for(southwest, northeast)
        for featured_info in featured_infos:
            try:
                featured_info['event'] = canonicalize_event_data(featured_info['event'], [], version)
                real_featured_infos.append(featured_info)
            except Exception as e:
                logging.exception("Error processing event %s: %s" % (result.event_id, e))
    except Exception as e:
        logging.exception("Error building featured event listing: %s", e)

    groupings = people_groupings(geocode, distance, skip_people=skip_people)
    query = {}
    if form:
        for field in form:
            query[field.name] = getattr(field, '_value', lambda: field.data)()

    if geocode:
        address_geocode = gmaps_api.lookup_address(geocode.formatted_address())
    else:
        address_geocode = None

    json_response = {
        'results': json_results,
        'onebox_links': onebox_links,
        'location': geocode.formatted_address() if geocode else None,
        'address': address.get_address_from_geocode(address_geocode),
        'query': query,
    }
    if groupings is not None:
        json_response['people'] = groupings
    if version <= (1, 3):
        json_response['featured'] = [x['event'] for x in real_featured_infos]
    else:
        json_response['featuredInfos'] = real_featured_infos
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
    return json_response


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

        groupings = people_groupings(geocode, distance, skip_people=False)
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
        if not form.location.data:
            if not form.keywords.data:
                self.add_error('Please enter a location or keywords')
        else:
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
            "Found %s keyword=%r events within %s %s of %s",
            len(search_results), form.keywords.data, form.distance.data, form.distance_units.data, form.location.data
        )

        # Keep in sync with mobile react code? And search_servlets
        skip_people = len(search_results) >= 10 or form.skip_people.data
        json_response = build_search_results_api(
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


def canonicalize_search_event_data(result, version):
    event_api = {}
    event_api['id'] = result.event_id
    event_api['name'] = result.data['name']
    event_api['slugged_name'] = slugify(unicode(result.data['name']))
    event_api['start_time'] = result.data['start_time']
    event_api['end_time'] = result.data['end_time']

    geocode = None
    if result.data['lng'] and result.data['lat']:
        geocode = {
            'longitude': result.data['lng'],
            'latitude': result.data['lat'],
        }
    event_api['venue'] = {
        'name': result.data.get('venue', {}).get('name', None),
        'geocode': geocode,
        'address': result.data.get('venue', {}).get('address', None),
    }
    if result.data.get('picture'):
        event_api['picture'] = {
            'source': urls.event_image_url(result.event_id),
            'width': result.data.get('picture', {}).get('width', 1),
            'height': result.data.get('picture', {}).get('height', 1),
        }
    else:
        event_api['picture'] = None

    annotations = {}
    annotations['keywords'] = result.data['keywords']
    annotations['categories'] = event_types.humanize_categories(result.data['categories'])
    event_api['annotations'] = annotations
    if result.data['attendee_count']:
        event_api['rsvp'] = {
            'attending_count': result.data['attendee_count'],
            'maybe_count': result.data.get('maybe_count', 0),
        }
    else:
        event_api['rsvp'] = None
    return event_api


def canonicalize_event_data(db_event, event_keywords, version):
    event_api = {}
    event_api['id'] = db_event.id
    event_api['name'] = db_event.name
    event_api['slugged_name'] = slugify(unicode(db_event.name))
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
    if db_event.has_image:
        if version >= (1, 3):
            if db_event.json_props:
                width = db_event.json_props['photo_width']
                height = db_event.json_props['photo_height']
            else:
                cover = db_event.largest_cover
                width = cover['width']
                height = cover['height']
            # Used by new react builds
            event_api['picture'] = {
                'source': urls.event_image_url(db_event.id),
                'width': width,
                'height': height,
            }
        else:
            if db_event.json_props:
                ratio = 1.0 * db_event.json_props['photo_width'] / db_event.json_props['photo_height']
            else:
                cover = db_event.cover_images[0]
                ratio = 1.0 * cover['width'] / cover['height']
            # Covers the most common screen sizes, according to Mixpanel:
            widths = reversed([320, 480, 720, 1080, 1440])
            cover_images = [{
                'source': urls.event_image_url(db_event.id, width=width),
                'width': width,
                'height': int(width / ratio)
            } for width in widths]

            # Used by old android and ios builds
            event_api['picture'] = urls.event_image_url(db_event.id, width=200, height=200)
            # Used by old react builds
            event_api['cover'] = {
                'cover_id': 'dummy',  # Android (v1.1) expects this value, even though it does nothing with it.
                'images': sorted(cover_images, key=lambda x: -x['height']),
            }
    else:
        event_api['picture'] = None
        event_api['cover'] = None

    if db_event.json_props and 'language' in db_event.json_props:
        event_api['language'] = db_event.json_props['language']
    else:
        # bwcompat that let's this work without the need to re-save
        text = '%s. %s' % (event_api['name'], event_api['description'])
        try:
            event_api['language'] = language.detect(text)
        except ValueError:
            logging.exception('Error detecting language on event %s with text %r', db_event.id, text)
            event_api['language'] = None

    # location data
    if db_event.location_name:
        venue_location_name = db_event.location_name
    else:
        # In these very rare cases (where we've manually set the location on a location-less event), return ''
        # TODO: We'd ideally like to return None, but unfortunately Android expects this to be non-null in 1.0.3 and earlier.
        venue_location_name = ""
    venue = db_event.venue
    if 'name' in venue and venue['name'] != venue_location_name:
        logging.error(
            "For event %s, venue name %r is different from location name %r", db_event.fb_event_id, venue['name'], venue_location_name
        )
    venue_id = db_event.venue_id
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
            'creator': str(db_event.creating_fb_uid) if db_event.creating_fb_uid else None,  #STR_ID_MIGRATE
            'creatorName': db_event.creating_name if db_event.creating_name else None,  #STR_ID_MIGRATE
        }
    else:
        annotations['creation'] = None
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
    if db_event:  # TODO: When is this not true?
        annotations['categories'] = event_types.humanize_categories(db_event.auto_categories)

    event_api['annotations'] = annotations
    event_api['ticket_uri'] = db_event.ticket_uri
    # maybe handle: 'timezone', 'updated_time'
    # rsvp_fields = ['attending_count', 'declined_count', 'maybe_count', 'noreply_count']
    if db_event.attending_count or db_event.maybe_count:
        event_api['rsvp'] = {
            'attending_count': db_event.attending_count or 0,
            'maybe_count': db_event.maybe_count or 0,
        }
    else:
        event_api['rsvp'] = None

    return event_api


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
        add_entities.add_update_event(fb_event, self.fbl, creating_uid=self.fbl.fb_uid, creating_method=eventdata.CM_USER)
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

        json_data = canonicalize_event_data(db_event, None, self.version)

        # Ten minute expiry on data we return
        self.response.headers['Cache-Control'] = 'public, max-age=%s' % (10 * 60)
        self.write_json_success(json_data)

    post = get


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


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
