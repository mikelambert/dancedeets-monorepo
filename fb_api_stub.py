import json
import logging

from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

import fb_api

class FileBackedBatchLookup(fb_api.BatchLookup):
    def _fetch_object_keys(self, keys):
        fetched_objects = {}
        for key in keys:
            fetched_objects[key] = json.loads(open('test_data/FacebookCachedObject/%s' % self._string_key(key)).read())
        return fetched_objects

    def lookup_venue(self, venue_id):
        pass

    def data_for_venue(self, venue_id):
        return {'deleted': True}


class Stub(object):
    def activate(self):
        self.original_batch_lookup = fb_api.BatchLookup
        fb_api.BatchLookup = FileBackedBatchLookup
        import locations
        dummy_location = {
            'latlng': (0, 0),
            'address': '',
            'city': '',
        }
        locations.get_geocoded_location = lambda *args, **kwargs: dummy_location

    def deactivate(self):
        fb_api.BatchLookup = self.original_batch_lookup
