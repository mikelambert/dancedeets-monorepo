import datetime

import base_servlet
from search import search
from search import search_base
from util import urls

class LoginIfUnspecified(object):
    def requires_login(self):
        return False

class CalendarFeedHandler(LoginIfUnspecified, base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        fe_search_query = search_base.FrontendSearchQuery.create_from_request_and_user(self.request, self.user)
        search_query = search.SearchQuery.create_from_query(fe_search_query, start_end_query=True)
        search_results = search_query.get_search_results(self.fbl)

        json_results = []
        for result in search_results:
            start_time = result.start_time
            end_time = result.fake_end_time
            duration = end_time - start_time
            if duration > datetime.timedelta(days=5):
                end_time = start_time
            elif duration <= datetime.timedelta(days=1):
                end_time = start_time
            all_day = False
            title = '@ %s\n\n%s' % (result.actual_city_name, result.name)
            json_results.append(dict(
                id=result.fb_event_id,
                title=title,
                start=start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                end=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                url=urls.fb_event_url(result.fb_event_id),
                allDay=all_day,
            ))
        self.write_json_response(json_results)    

