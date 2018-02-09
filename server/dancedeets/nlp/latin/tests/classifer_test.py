# -*-*- encoding: utf-8 -*-*-

from dancedeets import fb_api
from dancedeets.nlp import event_classifier
from dancedeets.nlp.latin import classifier
from dancedeets.test_utils import unittest


class TestClassifier(unittest.TestCase):
    memory_memcache = False

    def setUp(self):
        super(TestClassifier, self).setUp()
        self.fbl = fb_api.FBLookup("dummyid", None)

    def get_event(self, event_id):
        return self.fbl.get(fb_api.LookupEvent, event_id)

    def assertEvent(self, event_id):
        fb_event = self.get_event(event_id)
        classified_event = event_classifier.get_classified_event(fb_event)
        data = classifier.is_dance_event(classified_event)
        self.assertTrue(data[0], data[1])

    def assertNotEvent(self, event_id):
        fb_event = self.get_event(event_id)
        classified_event = event_classifier.get_classified_event(fb_event)
        data = classifier.is_dance_event(classified_event)
        self.assertFalse(data[0], data[1])


class TestFoodSalsa(TestClassifier):
    def runTest(self):
        self.assertNotEvent('1837327442944312')


class TestLatinCompetition(TestClassifier):
    def runTest(self):
        self.assertEvent('151555808837731')
        self.assertEvent('1821516191478841')
        self.assertEvent('235945840191010')
        self.assertEvent('2092023671075343')
        self.assertEvent('1553984067995241')


if __name__ == '__main__':
    print unittest.main()
