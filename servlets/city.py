
import urllib

import base_servlet

from events import cities
from events import eventdata
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
            time_period = eventdata.TIME_FUTURE

        path_bits = self.request.path.split('/')
        city_name = urllib.unquote(path_bits[2])

        # if they only care about particular types, too bad, redirect them to the main page since we don't support that anymore
        if len(path_bits) >= 4:
            self.redirect('/'.join(path_bits[:-1]))

        query = search.SearchQuery(time_period=time_period, city_name=city_name)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)
        rsvp.decorate_with_rsvps(self.batch_lookup, search_results)
        past_results, present_results, grouped_results = search.group_results(search_results)
        if time_period == eventdata.TIME_FUTURE:
            present_results = past_results + present_results
            past_results = []

        self.display['closest_city'] = city_name
        view_params = dict(
            city_name=city_name,
        )
        self.display['past_view_url'] = '/events/relevant?ajax=1&past=1&%s' % '&'.join('%s=%s' % (k, v) for (k, v) in view_params.iteritems())
        self.display['calendar_view_url'] = '/calendar?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in view_params.iteritems())

        self.display['past_results'] = past_results
        self.display['ongoing_results'] = present_results
        self.display['grouped_upcoming_results'] = grouped_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        self.render_template('city')

