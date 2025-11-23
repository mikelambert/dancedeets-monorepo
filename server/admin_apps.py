"""Admin-authorized WSGI applications.

These wrap various WSGI applications with admin authorization middleware.
"""

import logging
from webob.cookies import RequestCookies

from dancedeets import admin
from dancedeets import facebook
from dancedeets import login_logic
from dancedeets.login_admin import authorize_middleware
from dancedeets.redirect_canonical import redirect_canonical
from dancedeets.util.deferred_handler import application as deferred_application
import main

# Note: MapReduce and Pipeline are no longer supported in App Engine Flexible.
# These have been removed:
# - google.appengine.ext.deferred.application -> dancedeets.util.deferred_handler.application
# - mapreduce.main.APP -> removed (use Cloud Dataflow instead)
# - pipeline_wrapper._APP -> removed (use Cloud Workflows instead)


def _get_facebook_user_id(environ):
    request_cookies = RequestCookies(environ)
    our_cookie_uid, set_by_access_token_param = (
        login_logic.get_uid_from_user_login_cookie(request_cookies)
    )
    logging.info("Got request with user id: %s", our_cookie_uid)
    return our_cookie_uid


admin_ids = ["701004", "1199838260131297"]


def is_admin(environ):
    # check if the fb-tokens we have correspond to one of our admin users
    return _get_facebook_user_id(environ) in admin_ids


def middleware(app):
    return redirect_canonical(
        authorize_middleware(app, is_admin), "dancedeets.com", "www.dancedeets.com"
    )


authorized_deferred_app = middleware(deferred_application)
authorized_main_app = middleware(main.application)
authorized_admin_app = middleware(admin.app)

# Legacy references - these handlers need to be migrated to Cloud alternatives
# For now, point them to the main app which will return 404 for unhandled routes
authorized_pipeline_app = authorized_main_app
authorized_mapreduce_app = authorized_main_app
