import unittest
from webtest import TestApp

import main
from loc import gmaps_stub
from test_utils import fb_api_stub

app = TestApp(main.application)


class BaseTestSearch(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.gmaps_stub = gmaps_stub.Stub()
        self.gmaps_stub.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
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
        app.get('/?location=New York&distance=50')
