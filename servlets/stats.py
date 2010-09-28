import base_servlet
from logic import rankings

def compute_template_rankings(all_rankings, toplevel, time_period):
    style_rankings = []
    for style in toplevel:
        city_ranking = []
        for city, times_styles in all_rankings.iteritems():
            count = times_styles.get(time_period, {}).get(style, 0)
            if count:
                city_ranking.append(dict(city=city, count=count))
        city_ranking = sorted(city_ranking, key=lambda x: -x['count'])
        style_rankings.append(dict(style=style, ranking=city_ranking))
    return style_rankings

class RankingsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        time_period = self.request.get('time_period', rankings.ALL_TIME)
        style_event_rankings = compute_template_rankings(rankings.get_event_rankings(), rankings.STYLES, time_period)
        style_user_rankings = compute_template_rankings(rankings.get_user_rankings(), rankings.PEOPLES, time_period)
        style_dancer_rankings = [x for x in style_user_rankings if x['style'] in rankings.DANCERS]
        style_fan_rankings = [x for x in style_user_rankings if x['style'] in rankings.FANS]
        self.display['style_event_rankings'] = style_event_rankings
        self.display['style_dancer_rankings'] = style_dancer_rankings
        self.display['style_fan_rankings'] = style_fan_rankings
        self.display['time_periods'] = rankings.TIME_PERIODS
        self.display['current_time_period'] = time_period
        self.display['user_city'] = self.user.get_closest_city().key().name()
        self.display['string_translations'] = rankings.string_translations

        self.render_template('rankings')
