import datetime
import logging

import base_servlet
from events import eventdata
from events import users
import locations
from logic import search
from util import urls

class LoginIfUnspecified(object):
    def requires_login(self):
        return False

class CalendarHandler(LoginIfUnspecified, base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        self.display['calendar_feed_url'] = '/calendar/feed?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())
        self.render_template('calendar_shell')

class CalendarFeedHandler(LoginIfUnspecified, base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        if self.request.get('start'):
            start_time = datetime.datetime.fromtimestamp(int(self.request.get('start')))
        else:
            start_time = datetime.datetime.now()
        if self.request.get('end'):
            end_time = datetime.datetime.fromtimestamp(int(self.request.get('end')))
        else:
            end_time = datetime.datetime.now() + datetime.timedelta(days=365)

        city_name = None
        location = None
        distance = None
        distance_units = None
        distance_in_km = None
        latlng_location = None
        if self.request.get('city_name'):
            city_name = self.request.get('city_name')
        else:
            location = self.request.get('location', self.user and self.user.location)
            distance = int(self.request.get('distance', self.user and self.user.distance))
            distance_units = self.request.get('distance_units', self.user and self.user.distance_units)
            if distance_units == 'miles':
                distance_in_km = locations.miles_in_km(distance)
            else:
                distance_in_km = distance
            latlng_location = locations.get_geocoded_location(location)['latlng']
        dance_type = self.request.get('dance_type', self.user and self.user.dance_type) or users.DANCE_TYPES_LIST[0]['internal']

        query = search.SearchQuery(city_name=city_name, location=latlng_location, distance_in_km=distance_in_km, dance_type=dance_type, start_time=start_time, end_time=end_time)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)

        json_results = []
        for result in search_results:
            json_results.append(dict(
                id=result.fb_event['info']['id'],
                title=result.fb_event['info']['name'],
                start=eventdata.parse_fb_timestamp(result.fb_event['info']['start_time']).strftime('%Y-%m-%dT%H:%M:%SZ'),
                end=eventdata.parse_fb_timestamp(result.fb_event['info']['end_time']).strftime('%Y-%m-%dT%H:%M:%SZ'),
                url=urls.fb_event_url(result.fb_event['info']['id']),
            ))
        self.write_json_response(json_results)    

