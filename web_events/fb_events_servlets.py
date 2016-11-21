import logging
import keys

import app
from events import eventdata
from event_scraper import add_entities
import fb_api
from users import users
from util import urls
from . import web_events_servlets

@app.route('/web_events/upload_multi_fbevent')
class ClassMultiFbEventUploadHandler(web_events_servlets.JsonDataHandler):
    def post(self):
        if self.json_body['scrapinghub_key'] != keys.get('scrapinghub_key'):
            self.response.status = 403
            return

        fb_uid = '701004'
        user = users.User.get_by_id(fb_uid)
        fbl = fb_api.FBLookup(fb_uid, user.fb_access_token)

        for event_url in self.json_body['events']:
            event_id = urls.get_event_id_from_url(event_url)
            fb_event = fbl.get(fb_api.LookupEvent, event_id, allow_cache=False)
            try:
                add_entities.add_update_event(fb_event, fbl, creating_method=eventdata.CM_AUTO_WEB)
            except add_entities.AddEventException:
                logging.exception('Error adding event %s', event_id)
