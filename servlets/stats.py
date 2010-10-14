import base_servlet
from logic import rankings


class RankingsHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        time_period = self.request.get('time_period', rankings.ALL_TIME)
        style_event_rankings = rankings.compute_template_rankings(rankings.get_city_by_event_rankings(), rankings.STYLES, time_period)
        style_user_rankings = rankings.compute_template_rankings(rankings.get_city_by_user_rankings(), rankings.PEOPLES, time_period)
        style_dancer_rankings = [x for x in style_user_rankings if x['style'] in rankings.DANCERS]
        style_fan_rankings = [x for x in style_user_rankings if x['style'] in rankings.FANS]
        self.display['style_event_rankings'] = style_event_rankings
        self.display['style_dancer_rankings'] = style_dancer_rankings
        self.display['style_fan_rankings'] = style_fan_rankings
        self.display['time_periods'] = rankings.TIME_PERIODS
        self.display['current_time_period'] = time_period
        if self.user:
            closest_city = self.user.get_closest_city()
            if closest_city:
                self.display['user_city'] = closest_city.key().name()
        self.display['string_translations'] = rankings.string_translations

        self.render_template('rankings')
