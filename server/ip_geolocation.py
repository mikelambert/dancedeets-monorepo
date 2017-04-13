
import json
import logging
import urllib

from google.appengine.api import memcache
from google.cloud import datastore

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
    data = _get_cache(ip)
    if not data:
        url = 'http://ip-api.com/json/%s' % ip
        results = urllib.urlopen(url).read()
        data = json.loads(results)
        _save_cache(ip, data)
    return data

def get_location_string_for(ip, city=True):
    data = get_location_data_for(ip)
    if data['status'] == 'fail':
        logging.warning('Failure to geocode %r: %s', ip, data['message'])
        return ''
    location_components = []

    location_components.append(data['city'])
    if data['countryCode'] in ['US', 'CA']:
        location_components.append(data['region'])
    location_components.append(data['country'])

    location = ', '.join(x for x in location_components if x)
    return location
