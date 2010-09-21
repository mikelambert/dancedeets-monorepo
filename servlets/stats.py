import base_servlet
from logic import rankings

class RankingsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        all_rankings = rankings.get_rankings()
        style_rankings = []
        for style in rankings.STYLES:
            city_ranking = []
            for city, times_styles in all_rankings.iteritems():
                count = times_styles.get(rankings.ALL_TIME, {}).get(style, 0)
                city_ranking.append(dict(city=city, count=count))
            city_ranking = sorted(city_ranking, key=lambda x: -x['count'])
            style_rankings.append(dict(style=style, ranking=city_ranking))
        self.display['style_rankings'] = style_rankings
        self.render_template('rankings')
