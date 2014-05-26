from google.appengine.api import mail

import base_servlet

class HelpHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        self.render_template('feedback')

class FeedbackHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        self.render_template('feedback')

    def post(self):
        self.finish_preload()
        from_line = 'From: %s <%s>' % (
            self.fbl.fetched_data(self.fb_uid)['profile']['name'],
            self.fbl.fetched_data(self.fb_uid)['profile']['email']
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
