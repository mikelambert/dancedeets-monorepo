#!/usr/bin/python

import os

import runner

runner.setup()

import logging
logging.getLogger().setLevel(logging.DEBUG)
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
        body = r.unicode_normal_body
        # All events should have this, if they don't then maybe the React server is broken
        # *Don't* overwrite these pages with broken React server results,
        # or it will destroy the CSS we produce for our AMP pages. :(
        if 'Add to Calendar' not in body:
            raise Exception('Could not find generated HTML in result:')
        f = open(path, 'w')
        f.write(body)

    def runTest(self):
        event = fixtures.create_event()
        event.fb_event['info']['ticket_uri'] = 'http://www.eventbrite.com'
        event.fb_event['info']['attending_count'] = 10
        event.fb_event['info']['place'] = {
            'name': 'place name',
            'location': {
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'United States',
            }
        }
        event.fb_event['info']['admins'] = {
            "data": [{
                "id": "admin_id",
                "name": "admin"
            }],
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
        raise Exception('Errors generating amp files!')


if __name__ == '__main__':
    generateAmpPages()
