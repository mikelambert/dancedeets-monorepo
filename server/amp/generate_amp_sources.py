#!/usr/bin/python

import sys
sys.path.insert(0, 'lib')
sys.path.insert(0, '/Users/lambert/google-cloud-sdk/platform/google_appengine')
sys.path.insert(0, '/Users/lambert/google-cloud-sdk/lib/third_party')

import logging
import os
from unittest import result
from webtest import TestApp

from google.appengine.ext import testbed

import main
from test_utils import fixtures
from test_utils import unittest

app = TestApp(main.application)


class TestEvent(unittest.TestCase):
    def runTest(self):
        event = fixtures.create_event()
        r = app.get('/events/%s?amp=1' % event.fb_event_id)
        path = os.path.join(os.path.dirname(__file__), './generated/%s.html' % event.fb_event_id)
        f = open(path, 'w')
        f.write(r.unicode_normal_body)

def generateAmpPages():
    test = TestEvent()
    test.testbed = testbed.Testbed()
    test.testbed.activate()
    r = result.TestResult()
    test.run(r)
    if r.errors or r.failures:
        logging.error('Error generating amp files:')
        for test, error in r.errors:
            logging.error('%s: %s', test, error)
        for test, fail in r.failures:
            logging.error('%s: %s', test, fail)

if __name__ == '__main__':
    generateAmpPages()
