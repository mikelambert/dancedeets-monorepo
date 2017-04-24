#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Python client library for the Facebook Platform.

This client library is designed to support the Graph API and the official
Facebook JavaScript SDK, which is the canonical way to implement
Facebook authentication. Read more about the Graph API at
http://developers.facebook.com/docs/api. You can download the Facebook
JavaScript SDK at http://github.com/facebook/connect-js/.
"""

import base64
import cgi
import datetime
import hmac
import json
import logging
import os
import hashlib
import urllib
import yaml

from util import runtime

if runtime.is_local_appengine():
    filename = 'facebook-dev.yaml'
elif runtime.is_prod_appengine() or runtime.is_prod_appengine_mvms():
    filename = 'facebook-prod.yaml'
else:
    filename = 'facebook-test.yaml'


def load_yaml(filename):
    abs_filename = os.path.join(os.path.dirname(__file__), filename)
    return yaml.load(file(abs_filename, 'r'))

FACEBOOK_CONFIG = load_yaml(filename)
try:
    _PROD_FACEBOOK_CONFIG = load_yaml('facebook-prod.yaml')
except IOError as e:
    logging.info("Cannot find facebook-prod.yaml, using non-prod config: %s", e)
    _PROD_FACEBOOK_CONFIG = FACEBOOK_CONFIG.copy()

# This new code pulled from: https://gist.github.com/1190267
# aka: Hacked version of "official" (but now unsupported) Facebook Python SDK to support OAuth 2.0

def urlsafe_b64decode(str):
    """Perform Base 64 decoding for strings with missing padding."""

    l = len(str)
    pl = l % 4
    return base64.urlsafe_b64decode(str.ljust(l+pl, "="))


class SignedRequestError(Exception):
    pass

class AlreadyHasLongLivedToken(Exception):
    pass

def parse_signed_request(signed_request, secret):
    """
    Parse signed_request given by Facebook (usually via POST),
    decrypt with app secret.

    Arguments:
    signed_request -- Facebook's signed request given through POST
    secret -- Application's app_secret required to decrpyt signed_request
    """

    if "." in signed_request:
        esig, payload = signed_request.split(".")
    else:
        return {}

    sig = urlsafe_b64decode(str(esig))
    data = json.loads(urlsafe_b64decode(str(payload)))

    if not isinstance(data, dict):
        raise SignedRequestError("Pyload is not a json string!")
        return {}

    if data["algorithm"].upper() == "HMAC-SHA256":
        if hmac.new(secret, payload, hashlib.sha256).digest() == sig:
            return data

    else:
        raise SignedRequestError("Not HMAC-SHA256 encrypted!")

    return {}

def parse_signed_request_cookie(cookies):
    return parse_signed_request(cookies.get("fbsr_" + FACEBOOK_CONFIG['app_id'], ""), FACEBOOK_CONFIG['secret_key'])

def get_user_from_cookie(cookies):
    app_id = FACEBOOK_CONFIG['app_id']
    access_token = cookies.get("user_token_" + app_id, "")
    if not access_token:
        return None

    result = extend_access_token(access_token)
    fb_cookie_data = parse_signed_request_cookie(cookies)
    if 'user_id' in fb_cookie_data:
        result['uid'] = fb_cookie_data['user_id']
    return result

def extend_access_token(access_token):
    app_id = FACEBOOK_CONFIG['app_id']
    app_secret = FACEBOOK_CONFIG['secret_key']

    args = dict(
        client_id = app_id,
        client_secret = app_secret,
        grant_type = 'fb_exchange_token',
        fb_exchange_token = access_token
    )
    url = "https://graph.facebook.com/oauth/access_token?" + urllib.urlencode(args)
    file = urllib.urlopen(url)
    try:
        token_response = file.read()
    finally:
        file.close()
    parsed_response = json.loads(token_response)
    logging.info("token extension response: %r", parsed_response)

    if 'expires_in' in parsed_response:
        access_token_expires = datetime.datetime.now() + datetime.timedelta(seconds=int(parsed_response["expires_in"]))
    else:
        access_token_expires = None

    result = {
        'access_token': parsed_response["access_token"],
        'access_token_expires': access_token_expires,
    }
    return result

