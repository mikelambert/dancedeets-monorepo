# Necessary so unittest grabs the python unittest
from __future__ import absolute_import

import unittest

from google.appengine.ext import testbed

from loc import gmaps_stub
from test_utils import fb_api_stub

class TestCase(unittest.TestCase):
    def setUp(self):
        self.testbed.init_blobstore_stub()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        self.testbed.init_urlfetch_stub()
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.gmaps_stub = gmaps_stub.Stub()
        self.gmaps_stub.activate()
        #TODO(lambert): move this into some testbed wrapper code, or port upstream
        # This is a bug in the code versions between appengine and its libraries:
        # mapreduce requires a DEFAULT_VERSION_HOSTNAME
        self.testbed.setup_env(overwrite=True,
            DEFAULT_VERSION_HOSTNAME='localhost',
        )

    def tearDown(self):
        self.gmaps_stub.deactivate()
        self.fb_api.deactivate()

