
import urllib

import base_servlet

from events import cities
from events import eventdata
from events import tags
from events import users
from logic import rsvp
from logic import search

class CityHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        # TODO(lambert): include recent past events as well
        if 'Googlebot' in self.request.user_agent:
            time_period = None
        else:
            time_period = tags.TIME_FUTURE

        path_bits = self.request.path.split('/')
        city_name = urllib.unquote(path_bits[2])

        # handle additional path elements here
        dance_type = users.DANCE_TYPE_ALL_DANCE['internal']
        title_prefix = ''
        # if they only care about particular types, restrict appropriately
        if len(path_bits) >= 4:
            if path_bits[3] == 'freestyle':
                dance_type = users.DANCE_TYPE_FREESTYLE['internal']
                title_prefix = 'Freestyle'
            elif path_bits[3] == 'choreo':
                dance_type = users.DANCE_TYPE_CHOREO['internal']
                title_prefix = 'Hiphop Choreo'

        query = search.SearchQuery(time_period=time_period, city_name=city_name, dance_type=dance_type)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)
        rsvp.decorate_with_rsvps(self.batch_lookup, search_results)
        past_results, present_results, grouped_results = search.group_results(search_results)
        if time_period == tags.TIME_FUTURE:
            present_results = past_results + present_results
            past_results = []

        self.display['closest_city'] = city_name
        view_params = dict(
            dance_type=dance_type,
            city_name=city_name,
        )
        self.display['past_view_url'] = '/events/relevant?ajax=1&past=1&%s' % '&'.join('%s=%s' % (k, v) for (k, v) in view_params.iteritems())
        self.display['calendar_view_url'] = '/calendar?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in view_params.iteritems())

        self.display['title_prefix'] = title_prefix
        self.display['past_results'] = past_results
        self.display['ongoing_results'] = present_results
        self.display['grouped_upcoming_results'] = grouped_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        self.render_template('city')

