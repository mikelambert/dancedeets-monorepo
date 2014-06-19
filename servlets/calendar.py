import base_servlet
from logic import search
from logic import search_base
from util import dates
from util import urls

class LoginIfUnspecified(object):
    def requires_login(self):
        return False

class CalendarFeedHandler(LoginIfUnspecified, base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        fe_search_query = search_base.FrontendSearchQuery.create_from_request_and_user(self.request, self.user, city_name=self.request.get('city_name'))
        search_query = search.SearchQuery.create_from_query(fe_search_query, start_end_query=True)
        search_results = search_query.get_search_results(self.fbl)

        json_results = []
        for result in search_results:
            json_results.append(dict(
                id=result.fb_event['info']['id'],
                title=result.fb_event['info']['name'],
                start=dates.parse_fb_start_time(result.fb_event).strftime('%Y-%m-%dT%H:%M:%SZ'),
                end=dates.parse_fb_end_time(result.fb_event, need_result=True).strftime('%Y-%m-%dT%H:%M:%SZ'),
                url=urls.fb_event_url(result.fb_event['info']['id']),
            ))
        self.write_json_response(json_results)    

