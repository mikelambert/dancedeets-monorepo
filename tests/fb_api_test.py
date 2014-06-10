#!/usr/bin/python

import unittest
import re

import mock_memcache
import fb_api
from test_utils import fb_api_stub

class TestLookupUser(unittest.TestCase):
    def runTest(self):
        lookups = fb_api.LookupUser.get_lookups('id')
        self.assertEqual(lookups['profile'], '/id')
        self.assertEqual(lookups['friends'], '/id/friends')
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
        lookups = fb_api.LookupEvent.get_lookups('id')
        info_url = re.sub('fields=[^&]*', 'fields=X', lookups['info'])
        self.assertEqual(info_url, '/id?fields=X')
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

class TestFBAPI(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()

    def tearDown(self):
        self.fb_api.deactivate()

    def runTest(self):
        fb = fb_api.FBAPI('access_token')
        d = fb.fetch_keys([])
        self.assertEqual(d, {})

        fb_api.FBAPI.results = {
            '/uid': (200, {}),
            '/uid/events?since=yesterday': (200, {}),
            '/uid/friends': (200, {}),
            '/uid/permissions': (200, {}),
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

        fb_api.FBAPI.results = {
            '/uid': (500, {}),
            '/uid/events?since=yesterday': (200, {}),
            '/uid/friends': (200, {}),
            '/uid/permissions': (200, {}),
        }
        user_key = (fb_api.LookupUser, 'uid')
        d = fb.fetch_keys(set([user_key]))
        # We don't return incomplete objects at all, if a component errors-out on 500
        self.assertEqual(d, {})

        fb_api.FBAPI.results = {
            '/uid': (200, False),
            '/uid/events?since=yesterday': (200, False),
            '/uid/friends': (200, False),
            '/uid/permissions': (200, False),
        }
        user_key = (fb_api.LookupUser, 'uid')
        d = fb.fetch_keys(set([user_key]))
        self.assertEqual(d,
            {user_key: {
                'empty': fb_api.EMPTY_CAUSE_DELETED,
            }}
        )

        fb_api.FBAPI.results = {
            '/uid': (200, {'error_code': 100}),
            '/uid/events?since=yesterday': (200, {'error_code': 100}),
            '/uid/friends': (200, {'error_code': 100}),
            '/uid/permissions': (200, {'error_code': 100}),
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
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate(disk_db=False)

    def tearDown(self):
        self.fb_api.deactivate()

    def runTest(self):
        fbl = fb_api.FBLookup('uid', 'access_token')

        # Set up our facebook backend
        fb_api.FBAPI.results = {
            '/uid': (200, {}),
            '/uid/events?since=yesterday': (200, {}),
            '/uid/friends': (200, {}),
            '/uid/permissions': (200, {}),
        }
        # And fetching it then populates our memcache and db
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

        # Now remove our facebook backend, and test all our caches

        fb_api.FBAPI.results = {}
        fbl.clear_local_cache()

        # Check that if allow_cache=False, we cannot fetch anything
        fbl.allow_cache = False
        self.assertRaises(fb_api.NoFetchedDataException, fbl.get, fb_api.LookupUser, 'uid')
        fbl.allow_cache = True

        # Rely on memcache/dbcache to fulfill this request now
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

        # Clear memcache...
        user_key = (fb_api.LookupUser, 'uid')
        fbl.m.invalidate_keys([user_key])
        fbl.clear_local_cache()

        # Check that fetching with allow_db_cache=False, fails
        fbl.allow_dbcache = False
        self.assertRaises(fb_api.NoFetchedDataException, fbl.get, fb_api.LookupUser, 'uid')
        fbl.allow_dbcache = True

        # But allowing db cache still works (and repopulates memcache)
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

        # Clear dbcache, but still can work (because of memcache)
        fbl.db.invalidate_keys([user_key])
        fbl.clear_local_cache()

        # Without allowing memcache read, it fails
        fbl.allow_memcache_read = False
        self.assertRaises(fb_api.NoFetchedDataException, fbl.get, fb_api.LookupUser, 'uid')
        fbl.allow_memcache_read = True

        # But with memcache read, it works fine
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

        # Clear memcache, now that db is empty, data is entirely gone, and it no longer works
        fbl.m.invalidate_keys([user_key])
        fbl.clear_local_cache()
        self.assertRaises(fb_api.NoFetchedDataException, fbl.get, fb_api.LookupUser, 'uid')

class TestFBLookupProfile(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate(disk_db=False)

    def tearDown(self):
        self.fb_api.deactivate()

    def runTest(self):
        fbl = fb_api.FBLookup('uid', 'access_token')

        # Set up our facebook backend
        fb_api.FBAPI.results = {
            '/uid': (200, {}),
        }
        # And fetching it then populates our memcache and db
        result = fbl.get(fb_api.LookupProfile, 'uid')
        self.assertEqual(result,
            {
                'profile': {},
                'empty': None,
            }
        )

class TestFailureHandling(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate(disk_db=False)

    def tearDown(self):
        self.fb_api.deactivate()

    def runTest(self):
        fbl = fb_api.FBLookup('uid', 'access_token')
        fbl.allow_cache = False

        # Set up our facebook backend
        fields_str = '%2C'.join(fb_api.OBJ_EVENT_FIELDS)
        url = '/eid?fields=%s' % fields_str

        # Inaccessible event
        fb_api.FBAPI.results = {
            url:
                (400, {"error": {"message": "Unsupported get request.", "type": "GraphMethodException", "code": 100}}),
            '/fql?q=%0ASELECT%0Apic%2C+pic_big%2C+pic_small%2C%0Aall_members_count%0AFROM+event+WHERE+eid+%3D+eid%0A':
                (400, {"error": {"message": "Unsupported get request.", "type": "GraphMethodException", "code": 100}}),
        }

        result = fbl.get(fb_api.LookupEvent, 'eid')
        self.assertEqual(result['empty'], fb_api.EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS)
        fbl.clear_local_cache()

        # Partial timeout of optional field
        fb_api.FBAPI.results = {
            url:
                (200, {'id': 'eid'}),
            '/?fields=images&ids=%7Bresult%3Dinfo%3A%24.cover.cover_id%7D': None,
            '/fql?q=%0ASELECT%0Apic%2C+pic_big%2C+pic_small%2C%0Aall_members_count%0AFROM+event+WHERE+eid+%3D+eid%0A':
                (200, {}),
        }

        result = fbl.get(fb_api.LookupEvent, 'eid')
        self.assertEqual(result['info']['id'], 'eid')
        fbl.clear_local_cache()

        # Partial timeout of required field
        fb_api.FBAPI.results = {
            url:
                (200, {'id': 'eid'}),
            '/?fields=images&ids=%7Bresult%3Dinfo%3A%24.cover.cover_id%7D': None,
            '/fql?q=%0ASELECT%0Apic%2C+pic_big%2C+pic_small%2C%0Aall_members_count%0AFROM+event+WHERE+eid+%3D+eid%0A': None,
        }

        self.assertRaises(fb_api.NoFetchedDataException, fbl.get, fb_api.LookupUser, 'eid')
        fbl.clear_local_cache()

        # Event without a Cover field
        fb_api.FBAPI.results = {
            url:
                (200, {
                    "name": "Event Title",
                    "start_time": "2014-07-12T17:00:00-0400",
                    "id": "eid"
                }),
            '/?fields=images&ids=%7Bresult%3Dinfo%3A%24.cover.cover_id%7D':
                (400, {'error': {'message': 'Cannot specify an empty identifier', 'code': 2500, 'type': 'OAuthException'}}),
            '/fql?q=%0ASELECT%0Apic%2C+pic_big%2C+pic_small%2C%0Aall_members_count%0AFROM+event+WHERE+eid+%3D+eid%0A':
                (200, {
                    "data": [
                        {
                            "pic": "",
                            "all_members_count": 437,
                        }
                    ]
                }),
        }

        result = fbl.get(fb_api.LookupEvent, 'eid')
        self.assertEqual(result['empty'], None)
        self.assertEqual(result['info']['id'], 'eid')

        #TODO(lambert): Add token-expiration functionality tests.
        """
        {u'error': {u'message': u'Error validating access token: Session has expired on Jun 9, 2014 10:05am. The current time is Jun 9, 2014 10:32am.', u'code': 190, u'type': u'OAuthException', u'error_subcode': 463}}
        """


class TestMisc(unittest.TestCase):
    def runTest(self):
        self.assertEqual('/path?fields=a%2Cb', fb_api.LookupType.url('path', fields=['a', 'b']))
        self.assertEqual(True, fb_api.LookupEvent.use_access_token)
        self.assertEqual(False, fb_api.LookupProfile.use_access_token)
