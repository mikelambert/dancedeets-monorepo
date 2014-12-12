import unittest
from webtest import TestApp

from google.appengine.ext import testbed

import main
from test_utils import fb_api_stub

app = TestApp(main.application)


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        #TODO(lambert): move this into some testbed wrapper code, or port upstream
        # This is a bug in the code versions between appengine and its libraries:
        # mapreduce requires a DEFAULT_VERSION_HOSTNAME
        self.testbed.setup_env(overwrite=True,
            DEFAULT_VERSION_HOSTNAME='localhost',
        )


    def tearDown(self):
        self.testbed.deactivate()
        self.fb_api.deactivate()

class TestSearch(TestSearch):
    def runTest(self):
        app.get('/?location=New York&distance=50')
