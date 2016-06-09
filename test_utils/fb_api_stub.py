import json
from google.appengine.api import urlfetch

import fb_api

RESULT_TIMEOUT = 'RESULT_TIMEOUT'

EXPIRED_ACCESS_TOKEN = 'EXPIRED_ACCESS_TOKEN'

def get_object(string_key):
    return json.loads(open('test_data/FacebookCachedObject/%s' % string_key).read())

class Stub(object):
    def activate(self, memory_memcache=True, disk_db=True):
        self.real_fb_api = fb_api.FBAPI
        if memory_memcache:
            fb_api.FBAPI = MemoryFBAPI
            fb_api.FBAPI.do_timeout = False
            fb_api.FBAPI.results = {}
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
    def __init__(self, batch_list, use_access_token, expired_token, do_timeout):
        self.batch_list = batch_list
        self.use_access_token = use_access_token
        self.expired_token = expired_token
        self.do_timeout = do_timeout

    def get_result(self):
        results = []
        if self.do_timeout:
            raise urlfetch.DownloadError("Deadline exceeded while waiting for HTTP response from URL")
        elif self.expired_token:
            return FakeResult(400, {'error': {
                'message': u'Error validating access token: Session has expired on Jun 9, 2014 10:05am. The current time is Jun 9, 2014 10:32am.',
                'code': 190,
                'type': 'OAuthException',
                'error_subcode': 463
            }})
        else:
            urls = [x['relative_url'] for x in self.batch_list]
            for url in urls:
                if url in MemoryFBAPI.results:
                    result = MemoryFBAPI.results[url]
                    if result is RESULT_TIMEOUT:
                        status_code = None
                        content = None
                    else:
                        status_code, content = result
                else:
                    status_code = 404
                    content = None
                if status_code:
                    results.append(dict(code=status_code, body=json.dumps(content)))
                else:
                    results.append(None)
            return FakeResult(200, results)

class FakeResult(object):
    def __init__(self, status_code, results):
        self.status_code = status_code
        self.content = json.dumps(results)

class MemoryFBAPI(fb_api.FBAPI):
    results = {}
    do_timeout = False

    def post(*args, **kwargs):
        pass

    def _create_rpc_for_batch(self, batch_list, use_access_token):
        return FakeRPC(batch_list, use_access_token, self.access_token == EXPIRED_ACCESS_TOKEN, self.do_timeout)
