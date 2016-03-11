# -*-*- encoding: utf-8 -*-*-

import datetime
import unittest

from web_events.scraper.spiders import jp_dancelife

tests = {
    u"""2016年3月25日（金）
    OPEN 12:00
    CLOSE 19:00""":
    (datetime.datetime(2016, 3, 25, 12), datetime.datetime(2016, 3, 25, 19)),
    u"""2016/3/27（日曜）
    12:00～22:00""":
    (datetime.datetime(2016, 3, 27, 12), datetime.datetime(2016, 3, 27, 22)),
    u"""2016/3/26[SAT]
    13:00～20:30""":
    (datetime.datetime(2016, 3, 26, 13), datetime.datetime(2016, 3, 26, 20, 30)),
    u"""2016年3月5日(土)
    OPEN 12:00 START 13:00""":
    (datetime.datetime(2016, 3, 5, 12), None),
    # http://www.tokyo-dancelife.com/event/2016_03/29491.php
    u"""2016年3月5日(土)
    ...and later in the body/description:
    【日本代表決定戦】
    OPEN 14:30 START 15:00""":
    (datetime.datetime(2016, 3, 5, 14, 30), None),
    u"""2016年3月5日(土)""":
    (datetime.date(2016, 3, 5), None),
    u"""2016 3/13(sun）
    OPEN 15:00 START 15:30""":
    (datetime.datetime(2016, 3, 13, 15), None),
    u"""2016/4/2(土)
    18:00open/18:30star""":
    (datetime.datetime(2016, 4, 2, 18), None),
    u"""2016.04.23 (土)
    OPEN：14:00
    START：14:45
    CLOSE予定：20:00""":
    (datetime.datetime(2016, 4, 23, 14), datetime.datetime(2016, 4, 23, 20)),
}


class TestParseFbTimestamp(unittest.TestCase):
    def runTest(self):
        for test, expected_result in tests.iteritems():
            result = jp_dancelife.parse_date_times(test)
            self.assertEqual(result, expected_result)
