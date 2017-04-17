
import json
import logging
import os
import urllib

from google.appengine.api import memcache
from google.cloud import datastore

from util import runtime

if not runtime.is_appengine():
    # We need this for tests that use gcloud libraries, that need auth and app_identity.
    # They don't run with the gcloud credentials, so need this to figure out who they are.
    os.environ['APPLICATION_ID'] = 'dancedeets-hrd'

client = datastore.Client()

def _memkey(ip):
    return 'IpGeolocation: %s' % ip

def _dbkey(ip):
    return client.key('IpGeolocation', ip)

def _save_cache(ip, data):
    data_dump = json.dumps(data)

    memcache.set(_memkey(ip), data_dump, time=24 * 60 * 60)

    obj = datastore.Entity(key=_dbkey(ip), exclude_from_indexes=['data'])
    obj['data'] = data_dump
    client.put(obj)

def _get_cache(ip):
    data_dump = memcache.get(_memkey(ip))
    if not data_dump:
        obj = client.get(_dbkey(ip))
        if not obj:
            return None
        data_dump = obj['data']
    return json.loads(data_dump)

def get_location_data_for(ip):
    if not ip:
        return {}
    data = _get_cache(ip)
    if not data:
        url = 'http://freegeoip.net/json/%s' % ip
        results = urllib.urlopen(url).read()
        data = json.loads(results)
        _save_cache(ip, data)
    return data

def get_location_string_for(ip, city=True):
    data = get_location_data_for(ip)
    if not data:
        return ''
    if data['country_code'] == '':
        logging.warning('Failure to geocode %r: %s', ip, data)
        return ''
    location_components = []

    location_components.append(data['city'])
    if data['country_code'] in ['US', 'CA']:
        location_components.append(data['region_code'])
    location_components.append(data['country_name'])

    location = ', '.join(x for x in location_components if x)
    return location
