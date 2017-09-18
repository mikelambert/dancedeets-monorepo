#!/usr/bin/python

from __future__ import absolute_import

import json
import urllib
from dancedeets import facebook
from dancedeets.util import urls

FACEBOOK_CONFIG = None


def get_config():
    global FACEBOOK_CONFIG
    if not FACEBOOK_CONFIG:
        FACEBOOK_CONFIG = facebook.load_yaml('facebook-dev.yaml')
    return FACEBOOK_CONFIG


def search(**params):
    params = params.copy()
    if 'type' not in params:
        raise ValueError('Most pass type= argument')
    params['access_token'] = get_config()['app_access_token']
    result = urllib.urlopen('https://graph.facebook.com/v2.9/search?%s' % urls.urlencode(params)).read()
    return json.loads(result)
