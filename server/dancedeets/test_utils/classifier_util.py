from dancedeets import fb_api
from dancedeets.nlp import event_classifier
from . import unittest


class TestClassifier(unittest.TestCase):
    memory_memcache = False
    classifier_func = None

    def setUp(self):
        super(TestClassifier, self).setUp()
        self.fbl = fb_api.FBLookup("dummyid", unittest.get_local_access_token_for_testing())

    def get_event(self, event_id):
        return self.fbl.get(fb_api.LookupEvent, event_id)

    def assertEvent(self, event_id):
        fb_event = self.get_event(event_id)
        classified_event = event_classifier.get_classified_event(fb_event)
        data = self.classifier_func(classified_event)
        self.assertTrue(data[0], 'Failed on event %s: %s' % (event_id, data[1]))

    def assertNotEvent(self, event_id):
        fb_event = self.get_event(event_id)
        classified_event = event_classifier.get_classified_event(fb_event)
        data = self.classifier_func(classified_event)
        self.assertFalse(data[0], 'Failed on event %s: %s' % (event_id, data[1]))
