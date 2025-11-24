import logging
from webob.cookies import RequestCookies

import google.appengine.ext.deferred
from dancedeets.compat.mapreduce import main as mapreduce_main
from dancedeets import pipeline_wrapper

from dancedeets import admin
from dancedeets import facebook
from dancedeets import login_logic
from dancedeets.login_admin import authorize_middleware
from dancedeets.redirect_canonical import redirect_canonical
import main


def _get_facebook_user_id(environ):
    request_cookies = RequestCookies(environ)
    our_cookie_uid, set_by_access_token_param = login_logic.get_uid_from_user_login_cookie(request_cookies)
    logging.info('Got request with user id: %s', our_cookie_uid)
    return our_cookie_uid


admin_ids = ['701004', '1199838260131297']


def is_admin(environ):
    # check if the fb-tokens we have correspond to one of our admin users
    return _get_facebook_user_id(environ) in admin_ids


def middleware(app):
    return redirect_canonical(authorize_middleware(app, is_admin), 'dancedeets.com', 'www.dancedeets.com')


authorized_deferred_app = middleware(google.appengine.ext.deferred.application)
authorized_pipeline_app = middleware(pipeline_wrapper._APP)
authorized_mapreduce_app = middleware(mapreduce_main.APP)
authorized_main_app = middleware(main.application)
authorized_admin_app = middleware(admin.app)
