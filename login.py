#!/usr/bin/env python

import base_servlet
from events import users
        
class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        next = self.request.get('next') or '/'
        # if they somehow have a login token already, let's just send them there
        if self.facebook.access_token:
            user = users.get_user(self.facebook.uid)
            user.fb_session_key = self.facebook.session_key
            user.fb_access_token = self.facebook.access_token
            user.put()
            self.redirect(next)
        else:
            # Explicitly do not preload anything from facebook for this servlet
            # self.finish_preload()
            self.display['next'] = next
            self.display['api_key'] = self.facebook.api_key
            self.render_template('login')

