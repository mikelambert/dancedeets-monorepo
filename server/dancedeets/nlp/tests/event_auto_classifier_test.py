# -*-*- encoding: utf-8 -*-*-

import fb_api
from nlp import event_auto_classifier
from nlp import event_classifier
from nlp import rules
from test_utils import unittest


class TestSimpleMatches(unittest.TestCase):
    def runTest(self):
        self.assertTrue(rules.GOOD_DANCE.hack_double_regex()[1].findall('streetdance'))


class TestClassifier(unittest.TestCase):
    def setUp(self):
        super(TestClassifier, self).setUp()
        self.fbl = fb_api.FBLookup("dummyid", None)

    def get_event(self, event_id):
        return self.fbl.get(fb_api.LookupEvent, event_id)


class TestRockBattleEvent(TestClassifier):
    def runTest(self):
        fb_event = self.get_event('292568747504427')
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertTrue(is_battle)


class TestDJBattleEvent(TestClassifier):
    def runTest(self):
        fb_event = self.get_event('101883956566382')
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertFalse(is_battle)


class TestAllStylesBattleEvent(TestClassifier):
    def runTest(self):
        fb_event = self.get_event('113756888764413')
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertTrue(is_battle, reasons)


class TestMixtapeCompetitorList(TestClassifier):
    def runTest(self):
        fb_event = self.get_event('194555360659913')
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertFalse(is_battle)


class TestClass(TestClassifier):
    def runTest(self):
        fb_event = self.get_event('127125550747109')
        classified_event = event_classifier.get_classified_event(fb_event)
        has_classes, reasons = event_auto_classifier.has_list_of_good_classes(classified_event)
        self.assertTrue(has_classes)


class TestBadClub(TestClassifier):
    def runTest(self):
        fb_event = self.get_event('149083330948')
        classified_event = event_classifier.get_classified_event(fb_event)
        is_bad_club, reasons = event_auto_classifier.is_bad_club(classified_event)
        self.assertTrue(is_bad_club)


class TestBadDance(TestClassifier):
    def runTest(self):
        fb_event = self.get_event('170007276417905')
        classified_event = event_classifier.get_classified_event(fb_event)
        is_bad_dance, reasons = event_auto_classifier.is_bad_wrong_dance(classified_event)
        self.assertTrue(is_bad_dance)


class TestNoClass(TestClassifier):
    def runTest(self):
        fb_event = self.get_event('278853778841357')
        classified_event = event_classifier.get_classified_event(fb_event)
        has_classes, reasons = event_auto_classifier.has_list_of_good_classes(classified_event)
        self.assertFalse(has_classes)


class TestDanceBattle(TestClassifier):
    def runTest(self):
        fb_event = self.get_event('158496110883513')
        classified_event = event_classifier.get_classified_event(fb_event)
        is_battle, reasons = event_auto_classifier.is_battle(classified_event)
        self.assertTrue(is_battle)


if __name__ == '__main__':
    print unittest.main()
