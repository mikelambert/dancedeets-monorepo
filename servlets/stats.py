import base_servlet
from logic import rankings

def compute_template_rankings(all_rankings, toplevel):
    style_rankings = []
    for style in toplevel:
        city_ranking = []
        for city, times_styles in all_rankings.iteritems():
            count = times_styles.get(rankings.ALL_TIME, {}).get(style, 0)
            if count:
                city_ranking.append(dict(city=city, count=count))
        city_ranking = sorted(city_ranking, key=lambda x: -x['count'])
        style_rankings.append(dict(style=style, ranking=city_ranking))
    return style_rankings

class RankingsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        style_event_rankings = compute_template_rankings(rankings.get_event_rankings(), toplevel=rankings.STYLES)
        style_user_rankings = compute_template_rankings(rankings.get_user_rankings(), toplevel=rankings.PEOPLES)
        self.display['style_event_rankings'] = style_event_rankings
        self.display['style_user_rankings'] = style_user_rankings

        self.render_template('rankings')
