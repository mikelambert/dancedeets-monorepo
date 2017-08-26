import IPy
import json
import logging
import os
import time
import urllib

from google.appengine.api import memcache
from google.cloud import datastore

from util import runtime
from util import timelog


def generate_client():
    global client
    client = datastore.Client('dancedeets-hrd')


generate_client()


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
    start = time.time()
    data_dump = memcache.get(_memkey(ip))
    timelog.log_time_since('Getting IP Memcache', start)
    if not data_dump:
        start = time.time()
        obj = client.get(_dbkey(ip))
        timelog.log_time_since('Getting IP DBCache', start)
        if not obj:
            return None
        data_dump = obj['data']
    return json.loads(data_dump)


def get_location_data_for(ip):
    if not ip:
        return {}
    # Check the common private IP spaces (used by Google for sending requests)
    if IPy.IP(ip).iptype() == 'PRIVATE':
        return {}
    start = time.time()
    data = _get_cache(ip)
    timelog.log_time_since('Getting IP Cache', start)
    if not data:
        #TODO: consider using http://geoiplookup.net/ , which might offer better granularity/resolution
        url = 'http://freegeoip.net/json/%s' % ip
        start = time.time()
        results = urllib.urlopen(url).read()
        timelog.log_time_since('Getting IPData', start)
        data = json.loads(results)
        start = time.time()
        _save_cache(ip, data)
        timelog.log_time_since('Saving IPCache', start)
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
