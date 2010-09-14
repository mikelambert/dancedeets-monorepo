#!/usr/bin/env python

import datetime
import urllib

import base_servlet
from events import users
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

        
class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        next = self.request.get('next') or '/'
        # once they have a login token, do initial signin stuff, and redirect them
        if self.fb_uid:
            # We need to load the user info
            self.finish_preload()
            self.update_user_with_login()
            # Disabled due to an error: Only ancestor queries are allowed inside transactions.
            #db.run_in_transaction(self.update_user_with_login)
            self.redirect(next)
        else:
            # Explicitly do not preload anything from facebook for this servlet
            # self.finish_preload()
            self.display['next'] = '/login?%s' % urllib.urlencode({'next': next})
            self.display['api_key'] = base_servlet.FACEBOOK_CONFIG['api_key']
            self.render_template('login')

    def update_user_with_login(self):
        user = users.User.get(self.fb_uid)
        if not user:
            facebook_location = self.current_user()['profile']['location']['name']
            user = users.User.get_default_user(self.fb_uid, facebook_location)
        if not user.fb_access_token: # brand new user!
            user.creation_time = datetime.datetime.now()
            user_friends = users.UserFriendsAtSignup(key_name=str(self.fb_uid))
            user_friends.put()
            taskqueue.add(method='GET', url='/tasks/track_newuser_friends?' + urllib.urlencode({'user_id': self.fb_uid}))
        user.fb_access_token = self.fb_graph.access_token
        user.put()
        return user
