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
        use_url = 'ADMIN' if self.request.get('admin') else None
        event_rankings = rankings.compute_city_template_rankings(
            rankings.get_city_by_event_rankings(vertical),
            time_period,
            vertical=vertical,
            use_url=use_url,
        )
        user_rankings = rankings.compute_city_template_rankings(rankings.get_city_by_user_rankings(), time_period)

        self.display['admin'] = self.request.get('admin')

        self.display['vertical'] = vertical
        self.display['event_rankings'] = event_rankings
        self.display['user_rankings'] = user_rankings
        self.display['time_periods'] = rankings.TIME_PERIODS
        self.display['current_time_period'] = time_period

        self.display['string_translations'] = rankings.string_translations

        self.render_template('rankings')


@app.route('/tasks/compute_event_rankings')
class ComputeEventRankingsHandler(webapp2.RequestHandler):
    def get(self):
        vertical = self.request.get('vertical', 'STREET')
        rankings.begin_event_ranking_calculations(vertical)


@app.route('/tasks/compute_user_rankings')
class ComputeUserRankingsHandler(webapp2.RequestHandler):
    def get(self):
        rankings.begin_user_ranking_calculations()
