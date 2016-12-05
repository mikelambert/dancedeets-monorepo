#!/usr/bin/python

import sys
sys.path.insert(0, 'lib')
sys.path.insert(0, '/Users/lambert/google-cloud-sdk/platform/google_appengine')
sys.path.insert(0, '/Users/lambert/google-cloud-sdk/lib/third_party')

import logging
logging.getLogger().setLevel(logging.DEBUG)
import os
from unittest import result
from webtest import TestApp

from google.appengine.ext import testbed

from events import event_updates
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
        event.fb_event['info']['admins'] = {
          "data": [
            {
              "id": "admin_id",
              "name": "admin"
            }
          ],
          "paging": {
            "cursors": {
              "before": "",
              "after": ""
            }
          }
        }
        event.creating_fb_uid = 1
        event.creating_name = 'Addy McAdderson'
        event_updates.update_and_save_fb_events([(event, event.fb_event)])
        event.put()
        self.saveEvent(event)
        event = fixtures.create_web_event(json_body={'photo': 'test:http://url'})
        event.put()
        self.saveEvent(event)

def generateAmpPages():
    if not os.path.exists('amp/generated'):
        os.makedirs('amp/generated/')
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
