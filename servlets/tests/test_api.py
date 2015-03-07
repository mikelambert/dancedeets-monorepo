import unittest
import urllib

from webtest import TestApp
from webtest import utils

import fb_api
import main
from test_utils import fb_api_stub
from users import users

app = TestApp(main.application)


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        #TODO(lambert): move this into some testbed wrapper code, or port upstream
        # This is a bug in the code versions between appengine and its libraries:
        # mapreduce requires a DEFAULT_VERSION_HOSTNAME
        self.testbed.setup_env(overwrite=True,
            DEFAULT_VERSION_HOSTNAME='localhost',
        )

    def tearDown(self):
        self.fb_api.deactivate()


class TestAuth(TestSearch):
    def runTest(self):
        me_uid = '701004'
        access_token = 'BlahToken'
        new_access_token = 'BlahToken2'
        fb_api.FBAPI.results = {
            '/v1.0/me': (200, {'id': me_uid, 'name': 'Mike Lambert'}),
            '/v1.0/me/events?since=yesterday': (200, {}),
            '/v1.0/me/friends': (200, {}),
            '/v1.0/me/permissions': (200, {}),
        }

        auth_request = {
            'access_token': access_token,
            'access_token_expires': '2014-12-12T12:00:00-0500',
            'location': 'New Location',
            'client': 'android',
        }
        self.assertEqual(users.User.get_by_key_name(me_uid), None)
        result = app.post_json('/api/v1.0/auth', auth_request)
        self.assertEqual(result.json, {'success': True})
        self.assertNotEqual(users.User.get_by_key_name(me_uid), None)
        self.assertEqual(users.User.get_by_key_name(me_uid).fb_access_token, access_token)

        # Now again, but with fully-urlquoted string.
        # This time it will update the token, but not create a new user.
        old_dumps = utils.dumps
        try:
            utils.dumps = lambda *args, **kwargs: urllib.quote(old_dumps(*args, **kwargs))
            auth_request['access_token'] = new_access_token
            result = app.post_json('/api/v1.0/auth', auth_request)
            self.assertEqual(result.json, {'success': True})
        finally:
            utils.dumps = old_dumps

        self.assertNotEqual(users.User.get_by_key_name(me_uid), None)
        self.assertEqual(users.User.get_by_key_name(me_uid).fb_access_token, new_access_token)
