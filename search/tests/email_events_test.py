import unittest

import fb_api
from loc import gmaps_stub
from search import email_events
from test_utils import fb_api_stub
from test_utils import fixtures


class BaseTestSearch(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.gmaps_stub = gmaps_stub.Stub()
        self.gmaps_stub.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
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

class TestSearch(BaseTestSearch):
    def runTest(self):
        user = fixtures.create_user()
        event = fixtures.create_event()
        fixtures.index_events(self.testbed)

        fbl = user.get_fblookup()
        # Fetch it now so it's cached before email_for_user accesses it
        fbl.get(fb_api.LookupUser, user.fb_uid)

        message = email_events.email_for_user(user, fbl, should_send=False)
        self.assertIn('http://www.dancedeets.com/events/%s/' % event.fb_event_id, message.html)
        self.assertTrue(message, "Emailer did not email the user")
        
