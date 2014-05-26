import json
from google.appengine.api import urlfetch

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

        self.real_fb_api = fb_api.FBAPI
        fb_api.FBAPI = MemoryFBAPI

    def deactivate(self):
        fb_api.BatchLookup = self.original_batch_lookup

        fb_api.FBAPI = self.real_fb_api


class FakeRequest(object):
    def __init__(self, url):
        self._url = url
    def url(self):
        return self._url

class FakeRPC(object):
    def __init__(self, url, fb_api_results):
        self.url = url
        self.fb_api_results = fb_api_results
        self.request = FakeRequest(url)

    def get_result(self):
        if self.url in self.fb_api_results:
            status_code, content = self.fb_api_results[self.url]
            return FakeResult(status_code, content)
        else:
            raise urlfetch.DownloadError('no backend data found')

class FakeResult(object):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = json.dumps(content)

class MemoryFBAPI(fb_api.FBAPI):
        def __self__(self):
            self.results = {}

        def _create_rpc_for_url(self, url):
            return FakeRPC(url, self.results)
