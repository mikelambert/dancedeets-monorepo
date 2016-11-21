import logging
import keys

import app
from events import eventdata
from event_scraper import add_entities
import fb_api
from util import urls
from . import web_events_servlets

@app.route('/web_events/upload_multi_fbevent')
class ClassMultiFbEventUploadHandler(web_events_servlets.JsonDataHandler):
    def post(self):
        if self.json_body['scrapinghub_key'] != keys.get('scrapinghub_key'):
            self.response.status = 403
            return
        for event_url in self.json_body['events']:
            event_id = urls.get_event_id_from_url(self.request.get('event_url'))
            fb_event = self.fbl.get(fb_api.LookupEvent, event_id, allow_cache=False)
            add_entities.add_update_event(fb_event, self.fbl, creating_method=eventdata.CM_AUTO_WEB)

