import unittest
import urllib

from webtest import TestApp
from webtest import utils

import fb_api
from loc import gmaps_stub
import main
from test_utils import fb_api_stub
from test_utils import fixtures
from users import users

app = TestApp(main.application)


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.gmaps_stub = gmaps_stub.Stub()
        self.gmaps_stub.activate()
        self.testbed.init_memcache_stub()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        #TODO(lambert): move this into some testbed wrapper code, or port upstream
        # This is a bug in the code versions between appengine and its libraries:
        # mapreduce requires a DEFAULT_VERSION_HOSTNAME
        self.testbed.setup_env(overwrite=True,
            DEFAULT_VERSION_HOSTNAME='localhost',
        )

    def tearDown(self):
        self.fb_api.deactivate()
        self.gmaps_stub.deactivate()

class TestEvent(TestSearch):
    def runTest(self):
        event = fixtures.create_event()
        result = app.get('/api/v1.0/events/%s' % event.fb_event_id)
        self.assertEqual(result.json['id'], event.fb_event_id)

class TestAuth(TestSearch):
    def runTest(self):
        fields_str = '%2C'.join(fb_api.OBJ_USER_FIELDS)
        url = '/v2.2/me?fields=%s' % fields_str

        me_uid = '701004'
        access_token = 'BlahToken'
        new_access_token = 'BlahToken2'
        fb_api.FBAPI.results = {
            url: (200, {'id': me_uid, 'name': 'Mike Lambert'}),
            '/v2.2/me/events?since=yesterday': (200, {}),
            '/v2.2/me/friends': (200, {}),
            '/v2.2/me/permissions': (200, {}),
            '/v2.2/debug_token?input_token=BlahToken': (200, {
                'data': {'expires_at': 0}
                }),
            '/v2.2/debug_token?input_token=BlahToken2': (200, {
                'data': {'expires_at': 0}
                }),
        }

        auth_request = {
            'access_token': access_token,
            'access_token_expires': '2014-12-12T12:00:00-0500',
            'location': 'New Location',
            'client': 'android',
        }
        self.assertEqual(users.User.get_by_id(me_uid), None)
        result = app.post_json('/api/v1.0/auth', auth_request)
        self.assertEqual(result.json, {'success': True})
        self.assertNotEqual(users.User.get_by_id(me_uid), None)
        self.assertEqual(users.User.get_by_id(me_uid).fb_access_token, access_token)

        # Now again, but with fully-urlquoted string.
        # This time it will update the token, but not create a new user.
        old_dumps = utils.dumps
        try:
            utils.dumps = lambda *args, **kwargs: urllib.quote(old_dumps(*args, **kwargs))
            auth_request['access_token'] = new_access_token
            result = app.post_json('/api/v1.0/auth', auth_request)
            print result
            self.assertEqual(result.json, {'success': True})
        finally:
            utils.dumps = old_dumps

        self.assertNotEqual(users.User.get_by_id(me_uid), None)
        self.assertEqual(users.User.get_by_id(me_uid).fb_access_token, new_access_token)
