import json
import logging
import re
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
    return open('test_data/GMaps/%s' % string_key, 'w').write(json.dumps(json_data, indent=4, sort_keys=True))

CLEANUP_RE = re.compile(r'[^\w]')
def _geocode_key(**kwargs):
    if not kwargs:
        raise ValueError("Cannot pass empty parameters to gmaps fetch function! kwargs=%r", kwargs)
    new_kwargs = kwargs.copy()
    for k, v in new_kwargs.items():
        flattened_v = repr(v)
        flattened_v = CLEANUP_RE.sub('_', flattened_v)
        new_kwargs[k] = flattened_v[:30]
    joined = '_'.join(sorted('%s_%s' % (k, unicode(v).strip().lower()) for (k, v) in new_kwargs.items()))
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
