#!/usr/bin/python

import unittest
import re

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
        d = m.fetch_keys([])
        self.assertEqual(d, {})

        user_key = (fb_api.LookupUser, 'uid')
        user_key2 = (fb_api.LookupUser, 'uid2')
        d = m.fetch_keys([user_key])
        self.assertEqual(d, {})

        user = {'info': 'User Data'}
        m.save_objects({user_key: user})
        d = m.fetch_keys([user_key, user_key2])
        self.assertEqual(d, {user_key: user})

class TestDBCache(unittest.TestCase):
    def runTest(self):
        db = fb_api.DBCache('fetch_id')
        d = db.fetch_keys([])
        self.assertEqual(d, {})

        user_key = (fb_api.LookupUser, 'uid')
        user_key2 = (fb_api.LookupUser, 'uid2')
        d = db.fetch_keys([user_key])
        self.assertEqual(d, {})

        user = {'info': 'User Data'}
        db.save_objects({user_key: user})
        self.assertEqual(db.db_updates, 1)
        d = db.fetch_keys([user_key, user_key2])
        self.assertEqual(d, {user_key: user})

        user_modified = {'info': 'User Data Modified'}
        db.save_objects({user_key: user}) # no change, no update
        self.assertEqual(db.db_updates, 1)
        db.save_objects({user_key: user_modified})
        self.assertEqual(db.db_updates, 2)

class TestFBAPI(unittest.TestCase):
    def runTest(self):
        pass

class TestFBLookup(unittest.TestCase):
    def runTest(self):
        pass
