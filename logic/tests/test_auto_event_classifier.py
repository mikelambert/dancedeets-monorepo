# -*-*- encoding: utf-8 -*-*-

import unittest

from google.appengine.ext import testbed

import fb_api
from logic import event_auto_classifier
from logic import event_classifier
from test_utils import fb_api_stub

class TestSimpleMatches(unittest.TestCase):
        def runTest(self):
                self.assertTrue(event_auto_classifier.dance_regex[1].findall('streetdance'))

class TestClassifier(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.fbl = fb_api.FBLookup("dummyid", None)

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()
        self.fb_api.deactivate()

    def get_event(self, event_id):
        return self.fbl.get(fb_api.LookupEvent, event_id)

class TestRockBattleEvent(TestClassifier):
    def runTest(self):
        fb_event = self.get_event(292568747504427)
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertTrue(is_battle)

class TestDJBattleEvent(TestClassifier):
    def runTest(self):
        fb_event = self.get_event(101883956566382)
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertFalse(is_battle)

class TestAllStylesBattleEvent(TestClassifier):
    def runTest(self):
        fb_event = self.get_event(113756888764413)
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertTrue(is_battle)

class TestMixtapeCompetitorList(TestClassifier):
    def runTest(self):
        fb_event = self.get_event(194555360659913)
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertFalse(is_battle)

class TestClass(TestClassifier):
    def runTest(self):
        fb_event = self.get_event(127125550747109)
        classified_event = event_classifier.get_classified_event(fb_event)
        has_classes, reasons = event_auto_classifier.has_list_of_good_classes(classified_event)
        self.assertTrue(has_classes)

class TestBadClub(TestClassifier):
    def runTest(self):
        fb_event = self.get_event(149083330948)
        classified_event = event_classifier.get_classified_event(fb_event)
        is_bad_club, reasons = event_auto_classifier.is_bad_club(classified_event)
        self.assertTrue(is_bad_club)

class TestNoClass(TestClassifier):
    def runTest(self):
        fb_event = self.get_event(278853778841357)
        classified_event = event_classifier.get_classified_event(fb_event)
        has_classes, reasons = event_auto_classifier.has_list_of_good_classes(classified_event)
        self.assertFalse(has_classes)

class TestDanceBattle(TestClassifier):
    def runTest(self):
        fb_event = self.get_event(158496110883513)
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertTrue(is_battle)

if __name__ == '__main__':
    print unittest.main()
