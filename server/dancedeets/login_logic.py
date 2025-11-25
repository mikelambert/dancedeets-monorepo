import http.cookies
import hashlib
import json
import logging
import urllib.parse

from dancedeets import facebook


def get_login_cookie_name():
    return 'user_login_' + facebook.FACEBOOK_CONFIG['app_id']


def get_login_cookie(cookies):
    return cookies.get(get_login_cookie_name(), '')


def generate_userlogin_hash(user_login_cookie):
    raw_string = ','.join('%r: %r' % (k.encode('ascii'), v.encode('ascii')) for (k, v) in sorted(user_login_cookie.items()) if k != 'hash')
    m = hashlib.md5()
    m.update(facebook.FACEBOOK_CONFIG['secret_key'])
    m.update(raw_string)
    m.update(facebook.FACEBOOK_CONFIG['secret_key'])
    return m.hexdigest()


def validate_hashed_userlogin(user_login_cookie):
    passed_hash = user_login_cookie['hash']
    computed_hash = generate_userlogin_hash(user_login_cookie)
    if passed_hash != computed_hash:
        logging.error("For user_login_data %s, passed_in_hash %s != computed_hash %s", user_login_cookie, passed_hash, computed_hash)
    return passed_hash == computed_hash


def get_uid_from_user_login_cookie(cookies):
    """Load our dancedeets logged-in user/state"""
    our_cookie_uid = None
    set_by_access_token_param = None
    user_login_string = get_login_cookie(cookies)
    if user_login_string:
        user_login_cookie = json.loads(urllib.parse.unquote(user_login_string))
        logging.info("Got login cookie: %s", user_login_cookie)
        if validate_hashed_userlogin(user_login_cookie):
            our_cookie_uid = user_login_cookie['uid']
            set_by_access_token_param = user_login_cookie.get('access_token_md5')
    return our_cookie_uid, set_by_access_token_param


def get_uid_from_fb_cookie(cookies):
    # Load Facebook cookie
    try:
        response = facebook.parse_signed_request_cookie(cookies)
    except http.cookies.CookieError:
        logging.exception("Error processing cookie: %s")
        return
    fb_cookie_uid = None
    if response:
        fb_cookie_uid = response['user_id']
    logging.info("fb cookie id is %s", fb_cookie_uid)
    return fb_cookie_uid
