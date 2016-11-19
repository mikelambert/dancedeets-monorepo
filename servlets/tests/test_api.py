import urllib

from webtest import TestApp
from webtest import utils

import fb_api
import main
from test_utils import fixtures
from test_utils import unittest
from users import users

app = TestApp(main.application)


class TestEvent(unittest.TestCase):
    def runTest(self):
        event = fixtures.create_event()
        result = app.get('/api/v1.0/events/%s' % event.fb_event_id)
        if 'success' in result.json and not result.json['success']:
            self.fail(result.json)
        self.assertEqual(result.json['id'], event.fb_event_id)

class TestAuth(unittest.TestCase):
    def runTest(self):
        fields_str = '%2C'.join(fb_api.OBJ_USER_FIELDS)
        url = '/v2.2/me?fields=%s' % fields_str

        me_uid = '701004'
        access_token = 'BlahToken'
        new_access_token = 'BlahToken2'
        fb_api.FBAPI.results = {
            url: (200, {'id': me_uid, 'name': 'Mike Lambert'}),
            '/v2.2/me/events?since=yesterday&fields=id,rsvp_status&limit=5000': (200, {}),
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
            self.assertEqual(result.json, {'success': True})
        finally:
            utils.dumps = old_dumps

        self.assertNotEqual(users.User.get_by_id(me_uid), None)
        self.assertEqual(users.User.get_by_id(me_uid).fb_access_token, new_access_token)
