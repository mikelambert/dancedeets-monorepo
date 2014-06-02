import json
from google.appengine.api import urlfetch

import fb_api

def get_object(string_key):
    return json.loads(open('test_data/FacebookCachedObject/%s' % string_key).read())

class Stub(object):
    def activate(self, memory_memcache=True, disk_db=True):
        self.real_fb_api = fb_api.FBAPI
        if memory_memcache:
            fb_api.FBAPI = MemoryFBAPI
        self.real_db_cache = fb_api.DBCache
        if disk_db:
            fb_api.DBCache = DiskDBCache

    def deactivate(self):
        fb_api.FBAPI = self.real_fb_api
        fb_api.DBCache = self.real_db_cache

class DiskDBCache(fb_api.DBCache):
    def fetch_keys(self, keys):
        fetched_objects = {}
        for key in keys:
            try:
                fetched_objects[key] = get_object(self.key_to_cache_key(key))
            except IOError:
                pass
        return fetched_objects

class FakeRPC(object):
    def __init__(self, batch_list, use_access_token):
        self.batch_list = batch_list
        self.use_access_token = use_access_token

    def get_result(self):
        results = []
        if self.use_access_token:
            urls = [x['relative_url'] for x in self.batch_list]
            for url in urls:
                if url in MemoryFBAPI.results:
                    status_code, content = MemoryFBAPI.results[url]
                else:
                    status_code = 404
                    content = None
                results.append(dict(code=status_code, body=json.dumps(content)))
            return FakeResult(results)
        else:
            assert len(self.batch_list) == 1
            url = self.batch_list[0]['relative_url']
            if url in MemoryFBAPI.results:
                status_code, content = MemoryFBAPI.results[url]
                return FakeResult(content)
            else:
                raise urlfetch.DownloadError('no backend data found for %s' % url)

class FakeResult(object):
    def __init__(self, results):
        self.status_code = 200
        self.content = json.dumps(results)

class MemoryFBAPI(fb_api.FBAPI):
    results = {}

    def _create_rpc_for_batch(self, batch_list, use_access_token):
        return FakeRPC(batch_list, use_access_token)
