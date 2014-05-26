#!/usr/bin/python

import unittest
import json
import re

from google.appengine.api import urlfetch

import mock_memcache
import fb_api

class TestLookupUser(unittest.TestCase):
    def runTest(self):
        lookups = fb_api.LookupUser.get_lookups('id', 'access_token')
        self.assertEqual(lookups['profile'], 'https://graph.facebook.com/id?access_token=access_token')
        self.assertEqual(lookups['friends'], 'https://graph.facebook.com/id/friends?access_token=access_token')
        cache_key = fb_api.LookupUser.cache_key('id', 'fetch_id')
        self.assertEqual(cache_key, ('fetch_id', 'id', 'OBJ_USER'))

        object_data = {'info': 'User Info'}
        cleaned_object_data = fb_api.LookupUser.cleanup_data(object_data)
        self.assertEqual(cleaned_object_data['empty'], None)
        deleted_object_data = {'info': 'User Info', 'deleted': True}
        cleaned_object_data = fb_api.LookupUser.cleanup_data(deleted_object_data)
        self.assertEqual(cleaned_object_data['empty'], fb_api.EMPTY_CAUSE_DELETED)

class TestLookupEvent(unittest.TestCase):
    def runTest(self):
        lookups = fb_api.LookupEvent.get_lookups('id', 'access_token')
        info_url = re.sub('fields=[^&]*', 'fields=X', lookups['info'])
        self.assertEqual(info_url, 'https://graph.facebook.com/id?access_token=access_token&fields=X')
        cache_key = fb_api.LookupEvent.cache_key('id', 'fetch_id')
        self.assertEqual(cache_key, (fb_api.USERLESS_UID, 'id', 'OBJ_EVENT'))

        object_data = {'info': 'Event Info'}
        cleaned_object_data = fb_api.LookupEvent.cleanup_data(object_data)
        self.assertEqual(cleaned_object_data['empty'], None)
        deleted_object_data = {'info': 'Event Info', 'deleted': True}
        cleaned_object_data = fb_api.LookupEvent.cleanup_data(deleted_object_data)
        self.assertEqual(cleaned_object_data['empty'], fb_api.EMPTY_CAUSE_DELETED)

        object_data = {'fql_info': {'data': [{'all_members_count': 67}]}}
        cleaned_object_data = fb_api.LookupEvent.cleanup_data(object_data)
        self.assertEqual(cleaned_object_data['fql_info']['data'][0]['all_members_count'], 60)

        object_data = {'fql_info': {'data': [{'all_members_count': 267}]}}
        cleaned_object_data = fb_api.LookupEvent.cleanup_data(object_data)
        self.assertEqual(cleaned_object_data['fql_info']['data'][0]['all_members_count'], 200)

class TestMemcache(unittest.TestCase):
    def setUp(self):
        self.smemcache = fb_api.smemcache
        fb_api.smemcache = mock_memcache
    
    def tearDown(self):
        fb_api.smemcache = self.smemcache

    def runTest(self):
        m = fb_api.Memcache('fetch_id')
        d = m.fetch_keys(set())
        self.assertEqual(d, {})

        user_key = (fb_api.LookupUser, 'uid')
        user_key2 = (fb_api.LookupUser, 'uid2')
        d = m.fetch_keys(set([user_key]))
        self.assertEqual(d, {})

        user = {'info': 'User Data'}
        m.save_objects({user_key: user})
        d = m.fetch_keys(set([user_key, user_key2]))
        self.assertEqual(d, {user_key: user})

class TestDBCache(unittest.TestCase):
    def runTest(self):
        db = fb_api.DBCache('fetch_id')
        d = db.fetch_keys(set())
        self.assertEqual(d, {})

        user_key = (fb_api.LookupUser, 'uid')
        user_key2 = (fb_api.LookupUser, 'uid2')
        d = db.fetch_keys(set([user_key]))
        self.assertEqual(d, {})

        user = {'info': 'User Data'}
        db.save_objects({user_key: user})
        self.assertEqual(db.db_updates, 1)
        d = db.fetch_keys(set([user_key, user_key2]))
        self.assertEqual(d, {user_key: user})

        user_modified = {'info': 'User Data Modified'}
        db.save_objects({user_key: user}) # no change, no update
        self.assertEqual(db.db_updates, 1)
        db.save_objects({user_key: user_modified})
        self.assertEqual(db.db_updates, 2)

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

class TestFBAPI(unittest.TestCase):
    def setUp(self):
        self.rpc_for_url = fb_api.FBAPI._create_rpc_for_url
        self.fb_api_results = {}
        fb_api.FBAPI._create_rpc_for_url = lambda fbapi_self, url: FakeRPC(url, self.fb_api_results)

    def tearDown(self):
        fb_api.FBAPI._create_rpc_for_url = self.rpc_for_url

    def runTest(self):
        fb = fb_api.FBAPI('access_token')
        d = fb.fetch_keys([])
        self.assertEqual(d, {})

        self.fb_api_results = {
            'https://graph.facebook.com/uid?access_token=access_token': (200, {}),
            'https://graph.facebook.com/uid/events?since=yesterday?access_token=access_token': (200, {}),
            'https://graph.facebook.com/uid/friends?access_token=access_token': (200, {}),
            'https://graph.facebook.com/uid/permissions?access_token=access_token': (200, {}),
        }
        user_key = (fb_api.LookupUser, 'uid')
        d = fb.fetch_keys(set([user_key]))
        self.assertEqual(d,
            {user_key: {
                'empty': None,
                'friends': {},
                'permissions': {},
                'profile': {},
                'rsvp_for_future_events': {},
            }}
        )

        self.fb_api_results = {
            'https://graph.facebook.com/uid?access_token=access_token': (500, {}),
            'https://graph.facebook.com/uid/events?since=yesterday?access_token=access_token': (200, {}),
            'https://graph.facebook.com/uid/friends?access_token=access_token': (200, {}),
            'https://graph.facebook.com/uid/permissions?access_token=access_token': (200, {}),
        }
        user_key = (fb_api.LookupUser, 'uid')
        d = fb.fetch_keys(set([user_key]))
        # We don't return incomplete objects at all, if a component errors-out on 500
        self.assertEqual(d, {})

        self.fb_api_results = {
            'https://graph.facebook.com/uid?access_token=access_token': (200, False),
            'https://graph.facebook.com/uid/events?since=yesterday?access_token=access_token': (200, False),
            'https://graph.facebook.com/uid/friends?access_token=access_token': (200, False),
            'https://graph.facebook.com/uid/permissions?access_token=access_token': (200, False),
        }
        user_key = (fb_api.LookupUser, 'uid')
        d = fb.fetch_keys(set([user_key]))
        self.assertEqual(d,
            {user_key: {
                'empty': fb_api.EMPTY_CAUSE_DELETED,
            }}
        )

        self.fb_api_results = {
            'https://graph.facebook.com/uid?access_token=access_token': (200, {'error_code': 100}),
            'https://graph.facebook.com/uid/events?since=yesterday?access_token=access_token': (200, {'error_code': 100}),
            'https://graph.facebook.com/uid/friends?access_token=access_token': (200, {'error_code': 100}),
            'https://graph.facebook.com/uid/permissions?access_token=access_token': (200, {'error_code': 100}),
        }
        user_key = (fb_api.LookupUser, 'uid')
        d = fb.fetch_keys(set([user_key]))
        self.assertEqual(d,
            {user_key: {
                'empty': fb_api.EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS,
            }}
        )

class TestFBLookup(unittest.TestCase):
    def setUp(self):
        self.rpc_for_url = fb_api.FBAPI._create_rpc_for_url
        self.fb_api_results = {}
        fb_api.FBAPI._create_rpc_for_url = lambda fbapi_self, url: FakeRPC(url, self.fb_api_results)

    def tearDown(self):
        fb_api.FBAPI._create_rpc_for_url = self.rpc_for_url

    def runTest(self):
        fbl = fb_api.FBLookup('uid', 'access_token')

        self.fb_api_results = {
            'https://graph.facebook.com/uid?access_token=access_token': (200, {}),
            'https://graph.facebook.com/uid/events?since=yesterday?access_token=access_token': (200, {}),
            'https://graph.facebook.com/uid/friends?access_token=access_token': (200, {}),
            'https://graph.facebook.com/uid/permissions?access_token=access_token': (200, {}),
        }
        result = fbl.get(fb_api.LookupUser, 'uid')
        self.assertEqual(result,
            {
                'empty': None,
                'friends': {},
                'permissions': {},
                'profile': {},
                'rsvp_for_future_events': {},
            }
        )

        # Rely on cache to fulfill this request now
        self.fb_api_results = {}
        fbl.clear_local_cache()
        result = fbl.get(fb_api.LookupUser, 'uid')
        self.assertEqual(result,
            {
                'empty': None,
                'friends': {},
                'permissions': {},
                'profile': {},
                'rsvp_for_future_events': {},
            }
        )

        # Clear memcache, still works (and repopulates memcache)
        user_key = (fb_api.LookupUser, 'uid')
        fbl.m.invalidate_keys([user_key])
        fbl.clear_local_cache()
        result = fbl.get(fb_api.LookupUser, 'uid')
        self.assertEqual(result,
            {
                'empty': None,
                'friends': {},
                'permissions': {},
                'profile': {},
                'rsvp_for_future_events': {},
            }
        )

        # Clear db, still works (because of memcache)
        fbl.clear_local_cache()
        result = fbl.get(fb_api.LookupUser, 'uid')
        fbl.db.invalidate_keys([user_key])
        self.assertEqual(result,
            {
                'empty': None,
                'friends': {},
                'permissions': {},
                'profile': {},
                'rsvp_for_future_events': {},
            }
        )

        # Clear memcache, now that db is empty, no longer works
        fbl.m.invalidate_keys([user_key])
        fbl.clear_local_cache()
        self.assertRaises(fb_api.NoFetchedDataException, fbl.get, fb_api.LookupUser, 'uid')
