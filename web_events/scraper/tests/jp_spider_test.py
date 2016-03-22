# -*-*- encoding: utf-8 -*-*-

import datetime
import logging
import unittest

from web_events.scraper import jp_spider


class TestParseTimes(unittest.TestCase):
    tests = {
        u"""OPEN 12:00
        CLOSE 19:00""":
        (datetime.datetime(2016, 4, 1, 12), datetime.datetime(2016, 4, 1, 19)),
        u"""12:00～22:00""":
        (datetime.datetime(2016, 4, 1, 12), datetime.datetime(2016, 4, 1, 22)),
        u"""13:00～20:30""":
        (datetime.datetime(2016, 4, 1, 13), datetime.datetime(2016, 4, 1, 20, 30)),
        u"""OPEN 12:00 START 13:00""":
        (datetime.datetime(2016, 4, 1, 12), None),
        # http://www.tokyo-dancelife.com/event/2016_03/29491.php
        u"""【日本代表決定戦】
        OPEN 14:30 START 15:00""":
        (datetime.datetime(2016, 4, 1, 14, 30), None),
        u"""OPEN 15:00 START 15:30""":
        (datetime.datetime(2016, 4, 1, 15), None),
        u"""18:00open/18:30star""":
        (datetime.datetime(2016, 4, 1, 18), None),
        u"""OPEN：14:00
        START：14:45
        CLOSE予定：20:00""":
        (datetime.datetime(2016, 4, 1, 14), datetime.datetime(2016, 4, 1, 20)),
    }

    def runTest(self):
        for test, expected_result in self.tests.iteritems():
            logging.info("Testing: %s", test)
            result = jp_spider.parse_date_times(datetime.date(2016, 4, 1), test)
            self.assertEqual(result, expected_result, test)


class TestAtVenue(unittest.TestCase):
    tests = {
        u'@JANUS\n': 'JANUS',
        u'@gmail.com\n': None,
        u'@some_twitter\n': None,
        u'@The Voodoo Lounge\n': 'The Voodoo Lounge',
    }

    def runTest(self):
        for test, expected_result in self.tests.iteritems():
            logging.info("Testing: %s", test)
            result = jp_spider.find_at_venue(test)
            self.assertEqual(result, expected_result, test)
