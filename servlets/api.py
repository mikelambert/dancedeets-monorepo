import datetime
import json
import logging
import re
import urllib
import xml.sax.saxutils

from google.appengine.api import taskqueue

import base_servlet
import fb_api
import locations
from loc import math
from events import eventdata
from events import users
from logic import event_locations
from logic import search
from logic import search_base
from logic import user_creation
from util import text
from util import urls

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

#TODO(lambert): move to webapp. Handle:
# finish_preload, get_location_from_headers, add_error, errors_are_fatal.
class ApiHandler(base_servlet.BaseRequestHandler):
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

    def handle_error_response(self, errors):
        self.write_json_error({'errors': errors})
        return True

    def initialize(self, request, response):
        super(ApiHandler, self).initialize(request, response)

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


class FeedHandler(ApiHandler):

    def get(self):
        self.finish_preload()

        # Search API explicitly uses user=None
        fe_search_query = search_base.FrontendSearchQuery.create_from_request_and_user(self.request, None)

        if not fe_search_query.location:
            self.add_error('Need location parameter')
        format = self.request.get('format', 'json')
        if format not in ('json', 'atom'):
            self.add_error('Unknown format')
        self.errors_are_fatal()

        search_query = search.SearchQuery.create_from_query(fe_search_query)
        search_results = search_query.get_search_results(self.fbl)
        #TODO(lambert): move to common library.
        now = datetime.datetime.now() - datetime.timedelta(hours=12)
        search_results = [x for x in search_results if x.start_time > now]
        
        title = 'events near %(location)s.' % dict(
            distance=fe_search_query.distance,
            distance_units=fe_search_query.distance_units,
            location=fe_search_query.location,
        )
        if fe_search_query.keywords:
            title = '"%s" %s' % (fe_search_query.keywords, title)

        if format == 'atom':
            return self.handle_atom_feed(title, search_results)
        elif format == 'json':
            return self.handle_json_feed(title, search_results)
        else:
            logging.fatal("Unkonwn format, should have been caught up above")

    @staticmethod
    def SearchResultToJson(x):
        if x.fb_event['info'].get('location'):
            location = '%s, %s' % (x.fb_event['info']['location'], x.actual_city_name)
        else:
            location = x.actual_city_name
        return {
            'id': x.fb_event['info']['id'],
            'title': x.fb_event['info']['name'],
            'description': x.fb_event['info'].get('description'),
            'location': x.actual_city_name,
            'city': location,
            'image_url': x.get_image(),
            'cover_url': eventdata.get_largest_cover(x.fb_event),
            'start_time': x.start_time.strftime(DATETIME_FORMAT),
            'end_time': x.end_time and x.end_time.strftime(DATETIME_FORMAT) or None,
            'keywords': x.event_keywords_string(),
        }

    def handle_json_feed(self, title, search_results):
        json_results = [self.SearchResultToJson(x) for x in search_results]
        self.write_json_success(json_results)

    def handle_atom_feed(self, title, search_results):
        self.response.headers['Content-Type'] = 'application/atom+xml'

        last_modified = datetime.datetime.now().strftime(DATETIME_FORMAT)

        url = 'http://www.dancedeets.com/events/feed?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())

        self.response.out.write("""\
<?xml version="1.0" encoding="utf-8"?>

<feed xmlns="http://www.w3.org/2005/Atom">
 
    <title>%(title)s</title>
    <link href="%(url)s" rel="self" />
    <id>http://www.dancedeets.com</id>
    <updated>%(last_modified)s</updated>
    <author>
        <name>Dance Deets</name>
        <email>dancedeets@dancedeets.com</email>
    </author>
""" % dict(
            title=xml.sax.saxutils.escape(title),
            url=xml.sax.saxutils.escape(url),
            last_modified=last_modified,
        ))

        #TODO(lambert): setup proper date-modified times

        for result in search_results:
            location = event_locations.get_address_for_fb_event(result.fb_event) or 'Unknown'

            lines = []
            lines.append('<img src="%s" />' % urls.fb_event_image_url(result.fb_event['info']['id']))
            lines.append('Start Time: %s' % text.date_format(u'%Y-%m-%d %H:%M', result.start_time))
            if result.end_time:
                lines.append('End Time: %s' % text.date_format(u'%Y-%m-%d %H:%M', result.end_time))
            if location:
                lines.append('Location: %s' % xml.sax.saxutils.escape(location))
            lines.append('')
            lines.append(xml.sax.saxutils.escape(result.fb_event['info'].get('description', '')))
            description = '\n'.join(lines)

            description = description.replace('\n', '<br/>\n')
            self.response.out.write("""\
    <entry>
        <title>%(title)s</title>
        <link href="http://www.facebook.com/events/%(id)s/" />
        <id>http://www.dancedeets.com/event/%(id)s</id>
        <published>%(published)s</published>
        <summary type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">%(description)s</div></summary>
    </entry>
""" % dict(
                title=xml.sax.saxutils.escape(result.fb_event['info']['name'].encode('ascii', 'xmlcharrefreplace')),
                id=result.fb_event['info']['id'],
                published=result.start_time.strftime(DATETIME_FORMAT),
                description=(description.encode('ascii', 'xmlcharrefreplace')),
            ))

        self.response.out.write("""\
</feed>
""")

class SearchHandler(ApiHandler):

    def _get_title(self, location, keywords):
        if location:
            if keywords:
                return "Events with keywords %s" % keywords
            else:
                return "Events near %s" % location
        else:
            if keywords:
                return "Events with keywords %s" % keywords
            else:
                return "Events"

    def get(self, major_version, minor_version):
        self.finish_preload()

        # Search API explicitly uses user=None
        fe_search_query = search_base.FrontendSearchQuery.create_from_request_and_user(self.request, None)

        if not fe_search_query.location:
            city_name = None
            southwest = None
            northeast = None
            if not fe_search_query.keywords:
                if major_version == "1" and minor_version == "0":
                    self.write_json_success({'results': []})
                    return
                else:
                    self.add_error('Please enter a location or keywords')                
        else:
            if fe_search_query.distance_units == 'miles':
                distance_in_km = math.miles_in_km(fe_search_query.distance)
            else:
                distance_in_km = fe_search_query.distance
            southwest, northeast = locations.get_location_bounds(address=fe_search_query.location, distance_in_km=distance_in_km)
            if southwest and northeast:
                city_name = locations.get_name(address=fe_search_query.location)
                # This will fail on a bad location, so let's verify the location is geocodable above first.
            else:
                if major_version == "1" and minor_version == "0":
                    self.write_json_success({'results': []})
                    return
                else:
                    self.add_error('Could not geocode location')

        self.errors_are_fatal()

        search_query = search.SearchQuery.create_from_query(fe_search_query)

        # TODO(lambert): Increase the size limit when our clients can handle it. And improve our result sorting to return the 'best' results.
        search_query.limit = 500

        search_results = search_query.get_search_results(self.fbl)
        #TODO(lambert): move to common library.
        now = datetime.datetime.now() - datetime.timedelta(hours=12)
        search_results = [x for x in search_results if x.start_time > now]

        json_results = []
        for result in search_results:
            try:
                json_result = canonicalize_event_data(result.fb_event, None, result.event_keywords)
                json_results.append(json_result)
            except Exception as e:
                logging.error("Error processing event %s: %s" % (result.fb_event_id, e))

        title = self._get_title(city_name, fe_search_query.keywords)
        json_response = {
            'results': json_results,
            'title': title,
            'location': city_name
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


ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

class AuthHandler(ApiHandler):
    requires_auth = True

    def post(self):
        try:
            self.process()
        except:
            url = self.request.path
            body = self.request.body
            logging.info("Retrying URL %s", url)
            logging.info("With Payload %r", body)
            taskqueue.add(method='POST', url=url, payload=body,
                countdown=60*60)

    def process(self):
        self.errors_are_fatal()
        self.finish_preload()

        access_token = self.json_body.get('access_token')
        access_token_expires_with_tz = self.json_body.get('access_token_expires')
        if access_token_expires_with_tz:
            # strip off the timezone, since we can't easily process it
            # TODO(lambert): using http://labix.org/python-dateutil to parse timezones would help with that
            access_token_expires_without_tz = access_token_expires_with_tz[:-5]
            access_token_expires = datetime.datetime.strptime(access_token_expires_without_tz, ISO_DATETIME_FORMAT)
        else:
            access_token_expires = None
        location = self.json_body.get('location')
        # Don't use self.get_location_from_headers(), as I'm not sure how accurate it is if called from the API.
        # Also don't use location to update the user, if we don't actually have a location
        client = self.json_body.get('client')
        logging.info("Auth token from client %s is %s", client, access_token)

        user = users.User.get_by_key_name(str(self.fb_uid))
        if user:
            logging.info("User exists, updating user with new fb access token data")
            user.fb_access_token = access_token
            user.fb_access_token_expires = access_token_expires
            user.expired_oauth_token = False
            user.expired_oauth_token_reason = ""

            # Track usage stats
            user.last_login_time = datetime.datetime.now()
            if user.login_count:
                user.login_count += 1
            else:
                user.login_count = 2 # once for this one, once for initial creation
            if client not in user.clients:
                user.clients.append(client)


            if location:
                # If we had a geocode failure, or had a geocode bug, or we did a geocode bug and only got a country
                if not user.location or 'null' in user.location or ',' not in user.location or re.search(r', \w\w$', user.location):
                    user.location = location
            else:
                # Use the IP address headers if we've got nothing better
                if not user.location:
                    user.location = self.get_location_from_headers()

            user.put() # this also sets to memcache
        else:
            user_creation.create_user_with_fbuser(self.fb_uid, self.fb_user, access_token, access_token_expires, location, client=client)
        self.write_json_success()


class SettingsHandler(ApiHandler):
    requires_auth = True

    def get(self):
        user = users.User.get_by_key_name(str(self.fb_uid))
        json_data = {
            'location': user.location,
            'distance': user.distance,
            'distance_units': user.distance_units,
            'send_email': user.send_email,
        }
        self.write_json_success(json_data)

    def post(self):
        self.finish_preload()

        user = users.User.get_by_key_name(str(self.fb_uid))
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


def canonicalize_event_data(fb_event, db_event, event_keywords):
    event_api = {}
    for key in ['id', 'name', 'start_time']:
        event_api[key] = fb_event['info'][key]
    # Return an empty description, if we don't have a description for some reason
    event_api['description'] = fb_event['info'].get('description', '')
    # end time can be optional, especially on single-day events that are whole-day events
    event_api['end_time'] = fb_event['info'].get('end_time')

    # cover images
    if fb_event.get('cover_info'):
        cover_id = str(fb_event['info']['cover']['cover_id'])
        cover_images = sorted(fb_event['cover_info'][cover_id]['images'], key=lambda x: -x['height'])
        event_api['cover'] = {
            'cover_id': cover_id,
            'images': cover_images,
        }
    else:
        event_api['cover'] = None
    event_api['picture'] = eventdata.get_event_image_url(fb_event)

    # location data
    if 'location' in fb_event['info']:
        venue_location_name = fb_event['info']['location']
    # We could do something like this...
    #elif db_event and db_event.actual_city_name:
    #    venue_location_name = db_event.actual_city_name
    # ...but really, this would return the overridden/remapped address name, which would likely just be a "City" anyway.
    # A city isn't particularly useful for our clients trying to display the event on a map.
    else:
        # In these very rare cases (where we've manually set the location on a location-less event), return ''
        # TODO: We'd ideally like to return None, but unfortunately Android expects this to be non-null in 1.0.3 and earlier.
        venue_location_name = ""
    venue = fb_event['info'].get('venue', {})
    if 'name' in venue and venue['name'] != venue_location_name:
        logging.error("For event %s, venue name %r is different from location name %r", fb_event['info']['id'], venue['name'], venue_location_name)
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
    if 'longitude' in venue:
        geocode = {}
        for key in ['longitude', 'latitude']:
            geocode[key] = venue[key]
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
    if 'admins' in fb_event['info']:
        event_api['admins'] = fb_event['info']['admins']['data']
    else:
        event_api['admins'] =  None

    annotations = {}
    if db_event:
        annotations['creation'] = {
            'time': db_event.creation_time.strftime(DATETIME_FORMAT),
            'method': db_event.creating_method,
            'creator': db_event.creating_fb_uid,
        }
    # We may have keywords from the search result that called us
    if event_keywords:
        annotations['dance_keywords'] = event_keywords
    # or from the db_event associated with this
    elif db_event:
        annotations['dance_keywords'] = db_event.event_keywords
    # or possibly none at all, if we only received a fb_event..
    else:
        pass

    event_api['annotations'] = annotations
    # maybe handle: 'ticket_uri', 'timezone', 'updated_time', 'is_date_only'
    rsvp_fields = ['attending_count', 'declined_count', 'maybe_count', 'noreply_count', 'invited_count']
    event_api['rsvp'] = dict((x, fb_event['info'][x]) for x in rsvp_fields)

    return event_api

class EventHandler(ApiHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        path_bits = self.request.path.split('/events/')
        if len(path_bits) != 2:
            self.add_error('Path is malformed: %s' % self.request.path)
            self.response.out.write('Need an event_id.')
        else:
            try:
                event_id = str(int(path_bits[1].strip('/')))
            except TypeError:
                self.add_error('Event id expected: %s' % path_bits[1])

            fb_event = self.fbl.get(fb_api.LookupEvent, event_id)
            if fb_event['empty']:
                self.add_error('This event was %s.' % fb_event['empty'])

        self.errors_are_fatal()

        db_event = eventdata.DBEvent.get_by_key_name(event_id)

        json_data = canonicalize_event_data(fb_event, db_event, None)

        # Ten minute expiry on data we return
        self.response.headers['Cache-Control'] = 'max-age=%s' % (60*10)
        self.write_json_success(json_data)


