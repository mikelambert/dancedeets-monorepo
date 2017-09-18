#!/usr/bin/python

from __future__ import absolute_import

import json
import os
import re
import urllib
from dancedeets import facebook
from dancedeets.util import urls

try:
    os.makedirs('fb_cache')
except OSError:
    pass

FACEBOOK_CONFIG = None


def get_config():
    global FACEBOOK_CONFIG
    if not FACEBOOK_CONFIG:
        FACEBOOK_CONFIG = facebook.load_yaml('facebook-dev.yaml')
    return FACEBOOK_CONFIG

def _cache_name(params):
    name = '%s--%s' % (params['q'], params['center'])
    name = re.sub(r'[^-\w]', '_', name)
    print name
    return 'fb_cache/%s.txt' % name

def _get_cache(params):
    try:
        return json.loads(open(_cache_name(params)).read())
    except IOError:
        return None

def _set_cache(params, data):
    return open(_cache_name(params), 'w').write(json.dumps(data))

def fetch_all(self, city):
    all_businesses = []
    batch = 50
    i = 0
    while True:
        total, businesses = self._fetch_offset(city, i * batch, batch)
        all_businesses.extend(businesses)
        if i * batch + batch > total:
            break
        i += 1

    self._set_cache(city, all_businesses)
    return all_businesses

def search(**params):
    cached_result = _get_cache(params)
    if cached_result is not None:
        return json.loads(cached_result)

    new_params = params.copy()
    if 'type' not in new_params:
        raise ValueError('Most pass type= argument')
    new_params['access_token'] = get_config()['app_access_token']
    result = urllib.urlopen('https://graph.facebook.com/v2.9/search?%s' % urls.urlencode(new_params)).read()

    _set_cache(params, result)

    return json.loads(result)
