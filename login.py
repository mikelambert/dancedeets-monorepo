#!/usr/bin/env python

import datetime

import base_servlet
from events import users
from google.appengine.api.labs import taskqueue

        
class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        next = self.request.get('next') or '/'
        # once they have a login token, do initial signin stuff, and redirect them
        if self.facebook.access_token:
            user = users.get_user(self.facebook.uid)
            if not user.fb_session_key: # brand new user!
                user.creation_time = datetime.datetime.now()
                user_friends = users.UserFriendsAtSignup()
                user_friends.fb_uid = self.facebook.uid
                user_friends.put()
                taskqueue.add(url='/tasks/track_newuser_friends', params={'user_id': self.facebook.uid})
            user.fb_session_key = self.facebook.session_key
            user.fb_access_token = self.facebook.access_token
            user.put()
            self.redirect(next)
        else:
            # Explicitly do not preload anything from facebook for this servlet
            # self.finish_preload()
            self.display['next'] = '/login?%s' % urllib.urlencode({'next': next})
            self.display['api_key'] = self.facebook.api_key
            self.render_template('login')

