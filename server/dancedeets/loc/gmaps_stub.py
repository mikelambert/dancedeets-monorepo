import json
import logging
import re

from . import gmaps_api
from . import gmaps_backends

LOCATION_EXPIRY = 24 * 60 * 60
CLEANUP_RE = re.compile(r'[^\w]')


class StubCacheBackend(gmaps_backends.GMapsBackend):
    def __init__(self, backend):
        self.backend = backend

    @staticmethod
    def _get_object(string_key):
        filename = 'test_data/GMaps/%s' % string_key
        logging.info('Attempting to load file: %s', filename)
        return json.loads(open(filename).read())

    @staticmethod
    def _save_object(string_key, json_data):
        return open('test_data/GMaps/%s' % string_key, 'w').write(json.dumps(json_data, indent=4, sort_keys=True))

    @staticmethod
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

    def get_json(self, **kwargs):
        geocode_key = self._geocode_key(**kwargs)
        try:
            return self._get_object(geocode_key)
        except IOError:
            json_data = self.backend.get_json(**kwargs)
            self._save_object(geocode_key, json_data)
        return json_data


class Stub(object):
    def activate(self, memory_memcache=True, disk_db=True):
        self.orig_geocode_api = gmaps_api.geocode_api
        self.orig_places_api = gmaps_api.places_api
        gmaps_api.geocode_api = StubCacheBackend(gmaps_api.live_geocode_api)
        gmaps_api.places_api = StubCacheBackend(gmaps_api.live_places_api)

    def deactivate(self):
        gmaps_api.geocode_api = self.orig_geocode_api
        gmaps_api.places_api = self.orig_places_api
