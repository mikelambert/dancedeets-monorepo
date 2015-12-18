import json
import logging
import sys

from . import gmaps
from . import gmaps_api

gmaps_backend = None

LOCATION_EXPIRY = 24 * 60 * 60

def _get_object(string_key):
    filename = 'test_data/GMaps/%s' % string_key
    logging.info('Attempting to load file: %s', filename)
    return json.loads(open(filename).read())

def _save_object(string_key, json_data):
    return open('test_data/GMaps/%s' % string_key, 'w').write(json.dumps(json_data))

def _geocode_key(**kwargs):
    if not kwargs:
        raise ValueError("Cannot pass empty parameters to gmaps fetch function! kwargs=%r", kwargs)
    new_kwargs = kwargs.copy()
    for k, v in new_kwargs.items():
        byte_length = len(repr(v))
        if byte_length > 30:
            new_kwargs[k] = v[:len(v)*30/byte_length]
    joined = ','.join(sorted('%s=%r' % (k, unicode(v).strip().lower()) for (k, v) in new_kwargs.items()))
    joined = joined.replace("'", '_')
    return joined

def fetch_raw(**kwargs):
    geocode_key = _geocode_key(**kwargs)
    try:
        return _get_object(geocode_key)
    except IOError:
        json_data = gmaps.fetch_raw(**kwargs)
        _save_object(geocode_key, json_data)
    return json_data

def delete(**kwargs):
    pass

class Stub(object):
    def activate(self, memory_memcache=True, disk_db=True):
        global gmaps_backend
        gmaps_backend = gmaps_api.gmaps_backend
        gmaps_api.gmaps_backend = sys.modules[__name__]

    def deactivate(self):
        global gmaps_backend
        gmaps_api.gmaps_backend = gmaps_backend
