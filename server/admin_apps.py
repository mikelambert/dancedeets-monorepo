import logging
from webob.cookies import RequestCookies

import google.appengine.ext.deferred
import mapreduce.main
from dancedeets import pipeline_wrapper

from dancedeets import admin
from dancedeets import facebook
from dancedeets.login_admin import authorize_middleware
from dancedeets.redirect_canonical import redirect_canonical
import main


def _get_facebook_user_id(environ):
    request_cookies = RequestCookies(environ)
    user_data = facebook.parse_signed_request_cookie(request_cookies)
    user_id = user_data.get('user_id', None)
    logging.info('Got request with user id: %s', user_id)
    return user_id


admin_ids = ['701004', '1199838260131297']


def is_admin(environ):
    # check if the fb-tokens we have correspond to one of our admin users
    return _get_facebook_user_id(environ) in admin_ids


def middleware(app):
    return redirect_canonical(authorize_middleware(app, is_admin), 'dancedeets.com', 'www.dancedeets.com')


authorized_deferred_app = middleware(google.appengine.ext.deferred.application)
authorized_pipeline_app = middleware(pipeline_wrapper._APP)
authorized_mapreduce_app = middleware(mapreduce.main.APP)
authorized_main_app = middleware(main.application)
authorized_admin_app = middleware(admin.app)
