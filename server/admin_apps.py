import logging
from webob.cookies import RequestCookies

import google.appengine.ext.deferred
import mapreduce.main
import pipeline_wrapper

import admin
import facebook
from login_admin import authorize_middleware
import main


def _get_facebook_user_id(environ):
    request_cookies = RequestCookies(environ)
    user_data = facebook.parse_signed_request_cookie(request_cookies)
    user_id = user_data.get('user_id', None)
    logging.info('Got request with user id: %s', user_id)
    return user_id


admin_ids = ['701004']


def is_admin(environ):
    # check if the fb-tokens we have correspond to one of our admin users
    return _get_facebook_user_id(environ) in admin_ids


authorized_deferred_app = authorize_middleware(google.appengine.ext.deferred.application, is_admin)
authorized_deferred_app = authorize_middleware(google.appengine.ext.deferred.application, is_admin)
authorized_pipeline_app = authorize_middleware(pipeline_wrapper._APP, is_admin)
authorized_mapreduce_app = authorize_middleware(mapreduce.main.APP, is_admin)
authorized_main_app = authorize_middleware(main.application, is_admin)
authorized_admin_app = authorize_middleware(admin.app, is_admin)
