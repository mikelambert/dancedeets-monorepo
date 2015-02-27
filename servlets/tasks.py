
import logging

from google.appengine.api import mail

import base_servlet
import fb_api
from util import timings

# How long to wait before retrying on a failure. Intended to prevent hammering the server.
RETRY_ON_FAIL_DELAY = 60

class LoadFriendListHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        friend_list_id = self.request.get('friend_list_id')
        self.fbl.get(fb_api.LookupFriendList, friend_list_id)
    post=get

class TimingsKeepAlive(base_servlet.BaseTaskRequestHandler):
    def get(self):
        timings.keep_alive()

class TimingsProcessDay(base_servlet.BaseTaskRequestHandler):
    def get(self):
        summary = timings.summary()
        sorted_summary = sorted(summary.items(), key=lambda x: x[1])
        summary_lines = []
        for key, value in sorted_summary:
            summary_line = '%s: %sms' % (key, value)
            self.response.out.write('%s\n' % summary_line)
            logging.info(summary_line)
            summary_lines.append(summary_line)

        # email!
        if self.request.get('to') and self.request.get('sender'):
            mail.send_mail(
                to=self.request.get('to'),
                sender=self.request.get('sender'),
                subject="instance usage for the day",
                body='\n'.join(summary_lines)
            )
        timings.clear_all()

