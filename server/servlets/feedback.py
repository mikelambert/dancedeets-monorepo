import app
import base_servlet
import fb_api
from mail import mandrill_api


@app.route('/feedback')
class FeedbackHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        self.render_template('feedback')

    def post(self):
        self.finish_preload()
        fb_user = self.fbl.fetched_data(fb_api.LookupUser, self.fb_uid)
        from_line = 'From: %s <%s>' % (
            fb_user['profile']['name'],
            # Ugh, email is no longer a requied field ...?
            fb_user['profile'].get('email', 'User %s' % self.fb_uid),
        )
        subject = self.request.get('subject')
        body = '%s\n%s' % (from_line, self.request.get('body'))
        message = {
            'from_email': 'feedback@dancedeets.com',
            'from_name': 'DanceDeets Feedback Form',
            'subject': subject,
            'to': [{
                'email': 'feedback@dancedeets.com',
                'name': 'DanceDeets Feedback',
                'type': 'to',
            }],
            'text': body,
        }
        mandrill_api.send_message(message)
        self.user.add_message("Thanks, your message has been sent to DanceDeets!")
        self.redirect('/')
