import datetime
import logging

import base_servlet
from events import eventdata
import locations
from logic import search
from util import urls

class LoginIfUnspecified(object):
    def requires_login(self):
        if not self.user:
            # If they're not logged in, require a full set of fields...
            required_fields = ['freestyle', 'choreo']
            for field in required_fields:
                if not self.request.get(field):
                    return True
        return False

class CalendarHandler(LoginIfUnspecified, base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        self.display['calendar_feed_url'] = '/calendar/feed?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())
        self.render_template('calendar_shell')

class CalendarFeedHandler(LoginIfUnspecified, base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        start_time = datetime.datetime.fromtimestamp(int(self.request.get('start')))
        end_time = datetime.datetime.fromtimestamp(int(self.request.get('end')))

        city_name = None
        user_location = None
        distance = None
        distance_units = None
        distance_in_km = None
        latlng_user_location = None
        if self.request.get('city_name'):
            city_name = self.request.get('city_name')
        else:
            user_location = self.request.get('user_location', self.user and self.user.location)
            distance = int(self.request.get('distance', self.user and self.user.distance))
            distance_units = self.request.get('distance_units', self.user and self.user.distance_units)
            if distance_units == 'miles':
                distance_in_km = locations.miles_in_km(distance)
            else:
                distance_in_km = distance
            latlng_user_location = locations.get_geocoded_location(user_location)['latlng']
        freestyle = self.request.get('freestyle', self.user and self.user.freestyle)
        choreo = self.request.get('choreo', self.user and self.user.choreo)

        query = search.SearchQuery(city_name=city_name, location=latlng_user_location, distance_in_km=distance_in_km, freestyle=freestyle, choreo=choreo, start_time=start_time, end_time=end_time)
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

