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
        data = {'keywords': style}
        if not re.search('bot|crawl|spider', self.request.user_agent.lower()):
            data['location'] = self.get_location_from_headers(city=False)
        form = search_base.SearchForm(data=data)
        self.handle_search(form)
