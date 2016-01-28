from google.appengine.api import mail

import app
import base_servlet
import fb_api

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
            fb_user['profile']['email']
        )
        message = mail.EmailMessage(
            sender="DanceDeets Feedback Form <events@dancedeets.com>",
            subject=self.request.get('subject'),
            to='feedback@dancedeets.com',
            body='%s\n%s' % (from_line, self.request.get('body'))
        )
        message.send()

        self.user.add_message("Thanks, your message has been sent to DanceDeets!")
        self.redirect('/')
