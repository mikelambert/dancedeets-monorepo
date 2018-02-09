# -*-*- encoding: utf-8 -*-*-

from dancedeets import fb_api
from dancedeets.nlp import event_classifier
from dancedeets.nlp.latin import classifier
from dancedeets.test_utils import unittest


class TestClassifier(unittest.TestCase):
    memory_memcache = False

    def setUp(self):
        super(TestClassifier, self).setUp()
        self.fbl = fb_api.FBLookup("dummyid", unittest.get_local_access_token_for_testing())

    def get_event(self, event_id):
        return self.fbl.get(fb_api.LookupEvent, event_id)

    def assertEvent(self, event_id):
        fb_event = self.get_event(event_id)
        classified_event = event_classifier.get_classified_event(fb_event)
        data = classifier.is_salsa_event(classified_event)
        self.assertTrue(data[0], 'Failed on event %s: %s' % (event_id, data[1]))

    def assertNotEvent(self, event_id):
        fb_event = self.get_event(event_id)
        classified_event = event_classifier.get_classified_event(fb_event)
        data = classifier.is_salsa_event(classified_event)
        self.assertFalse(data[0], 'Failed on event %s: %s' % (event_id, data[1]))


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
        self.assertEvent('1422208217907436')
        self.assertEvent('344249636077753')
        self.assertEvent('165088020802863')


class TestLatinClass(TestClassifier):
    def runTest(self):
        self.assertEvent('154418185279514')
        self.assertEvent('176239869784234')
        self.assertEvent('141598903209252')
        self.assertEvent('1801249549949792')
        self.assertEvent('1819024858358233')
        self.assertEvent('192105941525864')
        self.assertEvent('958189144215292')
        self.assertEvent('313780035693230')
        self.assertEvent('10153148050940861')


# Salsa intermedia performance group
# self.assertEvent('710368129168209')
# dance contest, with salsa/bachata keywords
#        self.assertEvent('1765036530470368')

if __name__ == '__main__':
    print unittest.main()
