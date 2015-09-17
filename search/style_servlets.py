import re

import app
from . import search_base
from . import search_servlets

@app.route(r'/style/([\w-]+)/?')
class ShowStyleHandler(search_servlets.RelevantHandler):
    def requires_login(self):
        return False

    def handle(self, style):
        self.fbl.batch_fetch()
        fe_search_query = search_base.FrontendSearchQuery()
        fe_search_query.keywords = style
        if not re.search('bot|crawl|spider', self.request.user_agent.lower()):
            fe_search_query.location = self.get_location_from_headers(city=False)
        self.handle_search(fe_search_query)
