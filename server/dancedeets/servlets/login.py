#!/usr/bin/env python

import logging

from dancedeets import app
from dancedeets import base_servlet
from dancedeets.logic import mobile
from dancedeets.users import users


@app.route('/login')
class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def is_login_page(self):
        return True

    # TODO(lambert): move this into the same base / handler, so we don't do stupid redirects to /login
    def get(self):
        next_url = self.request.get('next') or '/'

        # If they're logged in, and have an account created, update and redirect
        if self.fb_uid:
            user = users.User.get_by_id(self.fb_uid)
            if user and not user.expired_oauth_token:
                self.redirect(next_url)
                return

        want_specific_page = (next_url != '/?')
        if want_specific_page:
            self.display['enable_page_level_ads'] = False
            self.display['next'] = next_url
            self.display['suppress_promos'] = True
            logging.info(self.display['next'])
            self.render_template('login_only')
            return

        # Treat them like a totally logged-out user since they have no user object yet
        self.fb_uid = None

        # Explicitly do not preload anything from facebook for this servlet
        # self.finish_preload()

        self.display['user_message'] = self.get_cookie('User-Message')

        from dancedeets.util import country_dialing_codes
        self.display['suppress_promos'] = True
        self.display['mobile_show_smartbanner'] = False

        self.display['next'] = next_url
        logging.info(self.display['next'])

        props = dict(
            mobilePlatform=self.display['mobile_platform'],
            mobileAppUrls={
                'android': mobile.ANDROID_URL,
                'ios': mobile.IOS_URL,
            },
            ipLocation=self.display['ip_location'],
        )
        self.setup_react_template('homepageReact.js', props)

        self.render_template('homepage_react')
