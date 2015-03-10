from . import search_base
from . import search_servlets

class ShowStyleHandler(search_servlets.RelevantHandler):
    def requires_login(self):
        return False

    def handle(self, style):
        self.fbl.batch_fetch()
        fe_search_query = search_base.FrontendSearchQuery()
        fe_search_query.keywords = style
        self.handle_search(fe_search_query)
