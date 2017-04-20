import hashlib
import hmac
import json
import logging
import pprint
import urllib
import webapp2

import app
import facebook
import fb_api
import keys
from users import users
from . import event_pipeline
from . import potential_events
from . import potential_events_reloading
from . import thing_db


# curl 'http://dev.dancedeets.com:8080/webhooks/user' --data '{"object": "user","entry":[{"changed_fields":["events"],"id": "701004"}]}'
# curl 'http://dev.dancedeets.com:8080/webhooks/user' --data '{"entry": [{"time": 1492571621, "changes": [{"field": "events", "value": {"event_id": 4444444444, "verb": "accept"}}], "id": "701004", "uid": "701004"}], "object": "user"}'
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
        logging.info('/webhooks/user called')
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
        logging.info("json_request: %s", json.dumps(json_body))
        if json_body['object'] == 'user':
            for entry in json_body['entry']:
                user_id = entry['uid']
                user = users.User.get_by_id(user_id)
                if not user:
                    logging.warning("Received webhook call for user id %s, but no User object.", user_id)
                event_ids = []
                for change in entry['changes']:
                    if change['field'] == 'events':
                        event_ids.append(unicode(change['value']['event_id']))

                discovered_list = []
                for event_id in event_ids:
                    de = potential_events.DiscoveredEvent(event_id, None, thing_db.FIELD_INVITES)
                    de.source_id = user_id
                    discovered_list.append(de)

                processed = False
                if user:
                    fbl = user.get_fblookup()
                    try:
                        event_pipeline.process_discovered_events(fbl, discovered_list)
                    except fb_api.ExpiredOAuthToken:
                        logging.info("Found ExpiredOAuthtoken when reloading events for User: %s", user.fb_uid)
                        logging.info("User's Clients: %s, Last Login: %s, Expiration: %s", user.clients, user.last_login_time, user.fb_access_token_expires)
                    else:
                        processed = True
                if not processed:
                    user = users.User.get_by_id('701004')
                    fbl = user.get_fblookup()
                    event_pipeline.process_discovered_events(fbl, discovered_list)
