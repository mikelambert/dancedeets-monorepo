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
    def saveEvent(self, event):
        r = app.get('/events/%s?amp=1' % event.id)
        path = os.path.join(os.path.dirname(__file__), './generated/%s.html' % event.id)
        f = open(path, 'w')
        f.write(r.unicode_normal_body)

    def runTest(self):
        event = fixtures.create_event()
        event.fb_event['info']['ticket_uri'] = 'http://www.eventbrite.com'
        event.fb_event['info']['attending_count'] = 10
        event.put()
        self.saveEvent(event)

        event = fixtures.create_web_event()
        event.put()
        self.saveEvent(event)

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
