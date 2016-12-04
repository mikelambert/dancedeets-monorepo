import logging
import sys
sys.path.insert(0, 'lib')
sys.path.insert(0, '/Users/lambert/google-cloud-sdk/platform/google_appengine')
sys.path.insert(0, '/Users/lambert/google-cloud-sdk/lib/third_party')

from webtest import TestApp
from webtest import utils

from google.appengine.ext import testbed

import main
from test_utils import fixtures
from test_utils import unittest

app = TestApp(main.application)


class TestEvent(unittest.TestCase):
    def runTest(self):
        event = fixtures.create_event()
        logging.error(1)
        result = app.get('/events/%s?amp=1' % event.fb_event_id)
        logging.error(result)

def generateAmpPages():
    test = TestEvent()
    test.testbed = testbed.Testbed()
    test.testbed.activate()
    test.run()

if __name__ == '__main__':
    generateAmpPages()
