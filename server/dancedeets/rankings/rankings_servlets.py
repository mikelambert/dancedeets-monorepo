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
        time_period = self.request.get('time_period', rankings.ALL_TIME)
        event_rankings = rankings.compute_city_template_rankings(rankings.get_city_by_event_rankings(), time_period)
        user_rankings = rankings.compute_city_template_rankings(rankings.get_city_by_user_rankings(), time_period)
        self.display['event_rankings'] = event_rankings
        self.display['user_rankings'] = user_rankings
        self.display['time_periods'] = rankings.TIME_PERIODS
        self.display['current_time_period'] = time_period

        self.display['string_translations'] = rankings.string_translations

        self.render_template('rankings')


@app.route('/tasks/compute_rankings')
class ComputeRankingsHandler(webapp2.RequestHandler):
    def get(self):
        rankings.begin_ranking_calculations()
