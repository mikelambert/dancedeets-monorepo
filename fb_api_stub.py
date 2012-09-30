import json
import logging

from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

import fb_api

class FileBackedBatchLookup(fb_api.BatchLookup):
    def _fetch_object_keys(self, keys):
        fetched_objects = {}
        for key in keys:
            try:
                fetched_objects[key] = get_object(self._string_key(key))
            except IOError:
                pass
        return fetched_objects

def get_object(string_key):
    return json.loads(open('test_data/FacebookCachedObject/%s' % string_key).read())

class Stub(object):
    def activate(self):
        self.original_batch_lookup = fb_api.BatchLookup
        fb_api.BatchLookup = FileBackedBatchLookup

    def deactivate(self):
        fb_api.BatchLookup = self.original_batch_lookup
