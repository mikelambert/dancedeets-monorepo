import json
import logging
import pprint
import urllib
import webapp2

import app
import facebook
import fb_api
import hashlib
import hmac
import keys
from . import potential_events_reloading
from users import users


# curl 'http://dev.dancedeets.com:8080/webhooks/user' --data '{"object": "user","entry":[{"changed_fields":["events"],"id": "701004"}]}'
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
        signature = self.request.headers.get('X_HUB_SIGNATURE')
        digest = hmac.new(facebook.FACEBOOK_CONFIG['secret_key'], self.request.body, hashlib.sha1).hexdigest()
        computed = 'sha1=%s' % digest
        if signature != computed:
            logging.error('Digest failed: Signature %s, Computed %s', signature, computed)

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
                try:
                    potential_events_reloading.load_potential_events_for_user(user)
                except fb_api.ExpiredOAuthToken:
                    logging.warning("Found ExpiredOAuthtoken when reloading events for User: %s", user.fb_uid)
                    logging.warning("User's Clients: %s, Last Login: %s, Expiration: %s", user.clients, user.last_login_time, user.fb_access_token_expires)
