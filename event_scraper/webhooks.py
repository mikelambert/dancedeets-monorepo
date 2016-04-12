import json
import logging
import pprint
import urllib
import webapp2

import app
import keys
from . import potential_events_reloading
from users import users


@app.route('/webhooks/user')
class WebhookPageHandler(webapp2.RequestHandler):
    def requires_login(self):
        return True

    def get(self):
        if self.request.get('hub.mode') == 'subscribe':
            if self.request.get('hub.verify_token') != keys.get('fb_webhook_verify_token'):
                logging.critical('Received invalid verify_token: %s', self.request.get('hub.verify_token'))
                return
            self.response.out.write(self.request.get('hub.challenge'))
        else:
            logging.critical('Unknown hub.mode received: %s', self.request.get('hub.mode'))

    def post(self):
        # TODO: Check X-Hub-Signature to verify validity
        if not self.request.body:
            logging.critical('No request.body to process')
            return

        logging.info("Request body: %r", self.request.body)
        escaped_body = urllib.unquote_plus(self.request.body.strip('='))
        json_body = json.loads(escaped_body)
        logging.info("json_request: %r", pprint.pformat(json_body))
        if json_body['object'] == 'user':
            user_ids = [x['id'] for x in json_body['entry'] if 'events' in x['changed_fields']]
            changed_users = users.User.get_by_ids(user_ids)
            for user in changed_users:
                potential_events_reloading.load_potential_events_for_user(user)
