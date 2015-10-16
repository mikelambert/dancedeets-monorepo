#!/usr/bin/env python

import logging

import app
import base_servlet
from logic import mobile
from users import users

@app.route('/login')
class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def is_login_page(self):
        return True

    #TODO(lambert): move this into the same base / handler, so we don't do stupid redirects to /login
    def get(self, needs_city=False):
        next = self.request.get('next') or '/'

        # If they're logged in, and have an account created, update and redirect
        if self.fb_uid:
            user = users.User.get_by_id(self.fb_uid)
            if user and not user.expired_oauth_token:
                self.redirect(next)
                return

        want_specific_page = (next != '/?')
        if want_specific_page:
            self.display['next'] = next
            self.display['suppress_promos'] = True
            logging.info(self.display['next'])
            self.render_template('login_only')
            return

        # Treat them like a totally logged-out user since they have no user object yet
        self.fb_uid = None

        # Explicitly do not preload anything from facebook for this servlet
        # self.finish_preload()

        self.display['user_message'] = self.get_cookie('User-Message')

        from util import country_dialing_codes
        self.display['suppress_promos'] = True
        self.display['country_codes'] = sorted(country_dialing_codes.mapping.items())
        self.display['android_url'] = mobile.ANDROID_URL
        self.display['ios_url'] = mobile.IOS_URL
        self.display['prefix'] = ''
        self.display['phone'] = '' # Set the default, and then let any errors-and-refilling occur on /mobile_apps
        self.display['mobile_show_smartbanner'] = False

        self.display['next'] = next
        logging.info(self.display['next'])
        self.display['needs_city'] = needs_city
        self.render_template('login')
