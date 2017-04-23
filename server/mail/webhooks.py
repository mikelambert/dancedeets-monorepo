import json
import logging
import webapp2

import app
import keys
from users import users


@app.route('/webhooks/mailchimp')
class MailchimpWebhookPageHandler(webapp2.RequestHandler):
    def handle(self):
        if self.request.get('secret_key') != keys.get('mailchimp_webhook_secret'):
            self.response.set_status(403)
            self.response.out.write('Forbidden: bad secret')
            return ''


@app.route('/webhooks/mandrill')
class MandrillWebhookPageHandler(webapp2.RequestHandler):
    def handle(self):
        logging.info('Mandrill webhook: %s', self.request)
        if self.request.get('secret_key') != keys.get('mandrill_webhook_secret'):
            logging.error('Got mandril webhook with bad secret: %s', self.request.get('secret_key'))
            self.response.set_status(403)
            self.response.out.write('Forbidden: bad secret')
            return

        if not self.request.get('mandrill_events'):
            logging.error('Got mandrill webhook without events')
            self.response.set_status(400)
            self.response.out.write('Bad Request: no mandrill_events')
            return


        mandrill_events = json.loads(self.request.get('mandrill_events'))

        for event in mandrill_events:
            if event['event'] in ['hard_bounce', 'spam', 'unsub', 'reject']:
                metadata = event['msg']['metadata']
                user_id = metadata['user_id']
                user = users.User.get_by_id(user_id)
                if metadata['email_type'] == 'weekly':
                    user.send_email = False
                user.put()
