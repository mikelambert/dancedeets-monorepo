import json
import logging
from dancedeets import keys
import urllib
import webapp2

from dancedeets import app
from dancedeets.events import eventdata
from dancedeets.events import event_updates
from dancedeets.pubsub import pubsub
from dancedeets.util import deferred


class JsonDataHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(JsonDataHandler, self).initialize(request, response)

        if self.request.body:
            escaped_body = urllib.unquote_plus(self.request.body.strip('='))
            self.json_body = json.loads(escaped_body)
        else:
            self.json_body = None


@app.route('/web_events/upload_multi')
class WebMultiUploadHandler(JsonDataHandler):
    def post(self):
        if self.json_body['scrapinghub_key'] != keys.get('scrapinghub_key'):
            self.response.status = 403
            return
        events_to_update = []
        new_ids = set()
        for json_body in self.json_body['items']:
            event_id = eventdata.DBEvent.generate_id(json_body['namespace'], json_body['namespaced_id'])
            e = eventdata.DBEvent.get_or_insert(event_id)
            if e.creating_method is None:
                new_ids.add(event_id)
            e.creating_method = eventdata.CM_WEB_SCRAPE
            events_to_update.append((e, json_body))

        event_updates.update_and_save_web_events(events_to_update)
        for event_id in new_ids:
            logging.info("New event, publishing to twitter/facebook: %s", event_id)
            deferred.defer(pubsub.eventually_publish_event, event_id)

        self.response.status = 200
