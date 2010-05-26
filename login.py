#!/usr/bin/env python

import base_servlet
from events import users
        
class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        # Explicitly do not preload anything from facebook for this servlet
        # self.finish_preload()
        self.display['next'] = self.request.get('next')
        self.display['api_key'] = self.facebook.api_key
        self.render_template('login')

