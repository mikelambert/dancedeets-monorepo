import json
import logging

from dancedeets import app
from dancedeets import keys
from dancedeets.events import event_emails
from dancedeets.mail import mailchimp_api
from dancedeets.users import users
from dancedeets.util.flask_adapter import BaseHandler
"""
type=upemail&fired_at=2017-04-23+08%3A08%3A31&data%5Bnew_id%5D=50696b797a&data%5Bnew_email%5D=mlambert%2Btest%40gmail.com&data%5Bold_email%5D=mlambert%40gmail.com&data%5Blist_id%5D=93ab23d636"
aka:
    type=upemail
    fired_at=2017-04-23+08:08:31
    data[new_id]=50696b797a
    data[new_email]=mlambert+test@gmail.com
    data[old_email]=mlambert@gmail.com
    data[list_id]=93ab23d636
"""


@app.route('/webhooks/mailchimp')
class MailchimpWebhookPageHandler(BaseHandler):
    def handle(self):
        logging.info('Mailchimp webhook: %s', self.request)
        if self.request.get('secret_key') != keys.get('mailchimp_webhook_secret'):
            self.response.set_status(403)
            self.response.out.write('Forbidden: bad secret')
            return ''

        # email update
        if self.request.get('type') == 'upemail':
            if self.request.get('data[list_id]') == mailchimp_api.LIST_ID:
                old_email = self.request.get('data[old_email]')
                new_email = self.request.get('data[new_email]')
                email_users = users.User.query(users.User.email == old_email).fetch(100)
                logging.info('Found %s users for old_email %s, updating to %s', len(email_users), old_email, new_email)
                for user in email_users:
                    user.email = new_email
                    user.put()
            else:
                logging.error('Unexpected webhook list_id: %s', self.request.get('data[list_id]'))
        else:
            logging.error('Unexpected webhook type: %s', self.request.get('type'))

    get = handle
    head = handle
    post = handle


@app.route('/webhooks/mandrill')
class MandrillWebhookPageHandler(BaseHandler):
    def handle(self):
        logging.info('Mandrill webhook: %s', self.request)
        if self.request.get('secret_key') != keys.get('mandrill_webhook_secret'):
            logging.error('Got mandrill webhook with bad secret: %s', self.request.get('secret_key'))
            self.response.set_status(403)
            self.response.out.write('Forbidden: bad secret')
            return

        if not self.request.get('mandrill_events'):
            logging.error('Got mandrill webhook without events')
            self.response.set_status(400)
            self.response.out.write('Bad Request: no mandrill_events')
            return

        mandrill_events = json.loads(self.request.get('mandrill_events'))

        logging.info('Processing %s webhook events', len(mandrill_events))
        for event in mandrill_events:
            if event['event'] in ['hard_bounce', 'spam', 'unsub', 'reject']:
                logging.info('Processing webhook event %s', event)
                metadata = event['msg']['metadata']
                if 'user_id' in metadata:
                    user_id = metadata['user_id']
                    user = users.User.get_by_id(user_id)
                    if metadata['email_type'] == 'weekly':
                        user.send_email = False
                        logging.info('Unsubscribing user %s (%s) in response to Mandrill %s', user.fb_uid, user.full_name, event['event'])
                    user.put()
                else:
                    email = event['msg']['email']
                    logging.info('Unsubscribing %s in response to Mandrill %s', email, event['event'])
                    event_emails.unsubscribe_email(email)

    get = handle
    head = handle
    post = handle
