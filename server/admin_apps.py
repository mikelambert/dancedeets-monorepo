from webob.cookies import RequestCookies

import google.appengine.ext.deferred
import mapreduce.main
import pipeline_wrapper

import admin
import facebook
from login_admin import authorize_middlware
import main

def _get_facebook_user_id(environ):
    request_cookies = RequestCookies(environ)
    print request_cookies
    user_data = facebook.parse_signed_request_cookie(request_cookies)
    print user_data
    return user_data.get('user_id', None)


admin_ids = ['701004']

def is_admin(environ):
    # check if the fb-tokens we have correspond to one of our admin users
    return _get_facebook_user_id(environ) in admin_ids


authorized_deferred_app = authorize_middlware(google.appengine.ext.deferred.application, is_admin)
authorized_pipeline_app = authorize_middlware(pipeline_wrapper._APP, is_admin)
authorized_mapreduce_app = authorize_middlware(mapreduce.main.APP, is_admin)
authorized_main_app = authorize_middlware(main.application, is_admin)
authorized_admin_app = authorize_middlware(admin.app, is_admin)
