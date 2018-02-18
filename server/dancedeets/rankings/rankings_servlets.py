import webapp2

from dancedeets import app
from dancedeets import base_servlet
from . import rankings


@app.route('/rankings')
class RankingsHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        vertical = self.request.get('vertical', 'STREET')
        time_period = self.request.get('time_period', rankings.ALL_TIME)
        event_rankings = rankings.compute_city_template_rankings(rankings.get_city_by_event_rankings(vertical), time_period)
        user_rankings = rankings.compute_city_template_rankings(rankings.get_city_by_user_rankings(vertical), time_period)

        self.display['vertical'] = vertical
        self.display['event_rankings'] = event_rankings
        self.display['user_rankings'] = user_rankings
        self.display['time_periods'] = rankings.TIME_PERIODS
        self.display['current_time_period'] = time_period

        self.display['string_translations'] = rankings.string_translations

        self.render_template('rankings')


@app.route('/tasks/compute_rankings')
class ComputeRankingsHandler(webapp2.RequestHandler):
    def get(self):
        vertical = self.request.get('vertical', 'STREET')
        rankings.begin_ranking_calculations(vertical)
