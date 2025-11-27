import json
import logging
import os
import requests

from dancedeets import fb_api

RESULT_TIMEOUT = 'RESULT_TIMEOUT'

EXPIRED_ACCESS_TOKEN = 'EXPIRED_ACCESS_TOKEN'

DEFAULT_CACHE_PATH = 'test_data/FacebookCachedObject'


def get_object(path, string_key):
    return json.loads(open(os.path.join(path, string_key)).read())


def save_object(path, string_key, data):
    return open(os.path.join(path, string_key), 'w').write(json.dumps(data))


class Stub(object):
    def activate(self, memory_memcache=True, disk_db=True, cache_path=None):
        self.real_fb_api = fb_api.FBAPI
        if memory_memcache:
            fb_api.FBAPI = MemoryFBAPI
            fb_api.FBAPI.do_timeout = False
            fb_api.FBAPI.results = {}
        self.real_db_cache = fb_api.DBCache
        if disk_db:
            fb_api.DBCache = create_disk_cache_function(cache_path or DEFAULT_CACHE_PATH)
        self.real_lookup_debug_tokens = fb_api.lookup_debug_tokens
        fb_api.lookup_debug_tokens = fake_lookup_debug_tokens

    def deactivate(self):
        fb_api.FBAPI = self.real_fb_api
        fb_api.DBCache = self.real_db_cache


class DiskDBCache(fb_api.DBCache):
    cache_path = None

    def __init__(self, *args, **kwargs):
        super(DiskDBCache, self).__init__(*args, **kwargs)

    def fetch_keys(self, keys):
        fetched_objects = {}
        for key in keys:
            try:
                fetched_objects[key] = get_object(self.cache_path, self.key_to_cache_key(key))
            except IOError:
                pass
        return fetched_objects

    def save_objects(self, keys_to_objects):
        if not keys_to_objects:
            return
        for k, v in keys_to_objects.items():
            if self._is_cacheable(k, v):
                cache_key = self.key_to_cache_key(k)
                save_object(self.cache_path, cache_key, v)


def create_disk_cache_function(cache_path):
    def disk_cache_constructor(uid):
        db_cache = DiskDBCache(uid)
        db_cache.cache_path = cache_path
        return db_cache

    return disk_cache_constructor


def fake_lookup_debug_tokens(tokens):
    return [{'empty': False, 'token': {'data': {'is_valid': True, 'expires_at': 0}}} for x in tokens]


class FakeRPC(object):
    def __init__(self, batch_list, use_access_token, expired_token, do_timeout):
        self.batch_list = batch_list
        self.use_access_token = use_access_token
        self.expired_token = expired_token
        self.do_timeout = do_timeout

    def get_result(self):
        results = []
        if self.do_timeout:
            raise requests.exceptions.Timeout("Deadline exceeded while waiting for HTTP response from URL")
        elif self.expired_token:
            return FakeResult(
                400, {
                    'error': {
                        'message': u'Error validating access token: Session has expired on Jun 9, 2014 10:05am. The current time is Jun 9, 2014 10:32am.',
                        'code': 190,
                        'type': 'OAuthException',
                        'error_subcode': 463
                    }
                }
            )
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
                    logging.error('Returning 404 because url %s not in %s', url, MemoryFBAPI.results)
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
    get_results = {}
    do_timeout = False

    def get(self, path, args):
        return self.get_results[path]

    def post(*args, **kwargs):
        pass

    def _create_rpc_for_batch(self, batch_list, use_access_token):
        return FakeRPC(batch_list, use_access_token, self.access_token_list == [EXPIRED_ACCESS_TOKEN],
                       self.do_timeout), EXPIRED_ACCESS_TOKEN
