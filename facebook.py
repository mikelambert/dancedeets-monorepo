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
import hmac
import json
import os
import hashlib
import urllib
import yaml

prod_mode = 'SERVER_SOFTWARE' in os.environ and not os.environ['SERVER_SOFTWARE'].startswith('Dev')
if prod_mode:
    filename = 'facebook-prod.yaml'
else:
    filename = 'facebook.yaml'
FACEBOOK_CONFIG = yaml.load(file(filename, 'r'))

# This new code pulled from: https://gist.github.com/1190267
# aka: Hacked version of "official" (but now unsupported) Facebook Python SDK to support OAuth 2.0

def urlsafe_b64decode(str):
    """Perform Base 64 decoding for strings with missing padding."""

    l = len(str)
    pl = l % 4
    return base64.urlsafe_b64decode(str.ljust(l+pl, "="))


class SignedRequestError(Exception):
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
    """Parses the cookie set by the official Facebook JavaScript SDK.

    cookies should be a dictionary-like object mapping cookie names to
    cookie values.

    If the user is logged in via Facebook, we return a dictionary with the
    keys "uid" and "access_token". The former is the user's Facebook ID,
    and the latter can be used to make authenticated requests to the Graph API.
    If the user is not logged in, we return None.

    Download the official Facebook JavaScript SDK at
    http://github.com/facebook/connect-js/. Read more about Facebook
    authentication at http://developers.facebook.com/docs/authentication/.
    """
    app_id = FACEBOOK_CONFIG['app_id']
    app_secret = FACEBOOK_CONFIG['secret_key']

    cookie = cookies.get("fbsr_" + app_id, "")
    if not cookie:
        return None

    try:
        int(cookie)
        # if it's an int, it's likely a cookie from after the user did FB.logout
        return None
    except ValueError:
        # if it's not an int, it's likely to be our encoded json string we want
        pass

    # TODO(lambert): LOGIN: If we pass in the access_token from the client, we dont need to query to get the code here...
    response = parse_signed_request(cookie, app_secret)
    import logging
    import datetime
    logging.info("cookie response is %r", response)
    if not response:
        return None

    args = dict(
        code = response['code'],
        client_id = app_id,
        client_secret = app_secret,
        redirect_uri = '',
    )

    url = "https://graph.facebook.com/oauth/access_token?" + urllib.urlencode(args)
    file = urllib.urlopen(url)
    try:
        token_response = file.read()
    finally:
        file.close()
    parsed_response = cgi.parse_qs(token_response)
    logging.info("token response %r", parsed_response)

    expires_time = None
    if 'access_token' in parsed_response:
      access_token = parsed_response["access_token"][-1]
      if 'expires' in parsed_response:
          expires_time = datetime.datetime.now() + datetime.timedelta(seconds=int(parsed_response["expires"][-1]))
    else:
      access_token = None

    if access_token:
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
        parsed_response = cgi.parse_qs(token_response)
        logging.info("token response #2 %r", parsed_response)
        if 'access_token' in parsed_response:
          access_token = parsed_response["access_token"][-1]
          if 'expires' in parsed_response:
              expires_time = datetime.datetime.now() + datetime.timedelta(seconds=int(parsed_response["expires"][-1]))
    
    # TODO(lambert): LOGIN: Do a sanity check that this access token belongs to this user? Every time??
    return dict(
        uid = response["user_id"],
        access_token = access_token,
        access_token_expires = expires_time,
    )

