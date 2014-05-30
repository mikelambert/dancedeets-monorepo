import datetime

import base_servlet
import locations
from logic import search
from util import dates
from util import urls

class LoginIfUnspecified(object):
    def requires_login(self):
        return False

#TODO(lambert): clean this out
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

        if self.request.get('city_name'):
            location = self.request.get('city_name')
            distance = 50
            distance_units = 'miles'
        else:
            location = self.request.get('location', self.user and self.user.location)
            distance = int(self.request.get('distance', self.user and self.user.distance or 50))
            distance_units = self.request.get('distance_units', self.user and self.user.distance_units or 'miles')
        if distance_units == 'miles':
            distance_in_km = locations.miles_in_km(distance)
        else:
            distance_in_km = distance
        bounds = locations.get_location_bounds(location, distance_in_km)

        keywords = self.request.get('keywords')
        min_attendees = int(self.request.get('min_attendees', self.user and self.user.min_attendees or 0))

        query = search.SearchQuery(bounds=bounds, start_time=start_time, end_time=end_time, min_attendees=min_attendees, keywords=keywords)
        search_results = query.get_search_results(self.fbl)

        json_results = []
        for result in search_results:
            json_results.append(dict(
                id=result.fb_event['info']['id'],
                title=result.fb_event['info']['name'],
                start=dates.parse_fb_start_time(result.fb_event).strftime('%Y-%m-%dT%H:%M:%SZ'),
                end=dates.parse_fb_end_time(result.fb_event, need_result=True).strftime('%Y-%m-%dT%H:%M:%SZ'),
                url=urls.fb_event_url(result.fb_event['info']['id']),
            ))
        self.write_json_response(json_results)    

