import webapp2

import app
import base_servlet
from . import cities
from . import rankings

@app.route('/rankings')
class RankingsHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        time_period = self.request.get('time_period', rankings.ALL_TIME)
        event_rankings = rankings.compute_city_template_rankings(rankings.get_city_by_event_rankings(), time_period)
        user_rankings = rankings.compute_city_template_rankings(rankings.get_city_by_user_rankings(), time_period)
        self.display['event_rankings'] = event_rankings
        self.display['user_rankings'] = user_rankings
        self.display['time_periods'] = rankings.TIME_PERIODS
        self.display['current_time_period'] = time_period
        if self.user and self.user.location:
            self.display['user_city'] = rankings.get_ranking_location(self.user.location)

        self.display['string_translations'] = rankings.string_translations

        self.render_template('rankings')

@app.route('/tools/import_cities')
class ImportCitiesHandler(webapp2.RequestHandler):
    def get(self):
        cities.import_cities()
        self.response.out.write("Imported Cities!")

@app.route('/tasks/compute_rankings')
class ComputeRankingsHandler(webapp2.RequestHandler):
    def get(self):
        rankings.begin_ranking_calculations()

