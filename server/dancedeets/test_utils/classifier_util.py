import logging
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

    def _run_event(self, event_id):
        fb_event = self.get_event(event_id)
        classified_event = event_classifier.get_classified_event(fb_event)
        data = self.classifier_func(classified_event)
        return data

    def assertEvent(self, event_id):
        data = self._run_event(event_id)
        self.assertTrue(data[0], 'Failed on event %s: %s' % (event_id, data[1]))

    def assertNotEvent(self, event_id):
        data = self._run_event(event_id)
        self.assertFalse(data[0], 'Failed on event %s: %s' % (event_id, data[1]))

    def _pass_fails(self, event_ids):
        passed = []
        failed = []
        for event_id in event_ids:
            data = self._run_event(event_id)
            if data[0]:
                passed.append(event_id)
            else:
                failed.append(event_id)
        return passed, failed

    def assertEvents(self, fraction, event_ids):
        passed, failed = self._pass_fails(event_ids)
        passed_fraction = 1.0 * len(passed) / len(event_ids)
        failed_fraction = 1.0 * len(failed) / len(event_ids)
        logging.info(
            'Ran on %s ids, %s(%s) passed, %s(%s) failed', len(event_ids), int(passed_fraction * 100), len(passed),
            int(failed_fraction * 100), len(failed)
        )
        for event_id in failed:
            data = self._run_event(event_id)
            logging.warning('Event failed: %s: %s', event_id, '\n'.join(data[1]))

        self.assertTrue(fraction <= passed_fraction, 'Too many events failed: %s of %s' % (len(failed), len(event_ids)))

    def assertNotEvents(self, fraction, event_ids):
        passed, failed = self._pass_fails(event_ids)
        passed_fraction = 1.0 * len(passed) / len(event_ids)
        failed_fraction = 1.0 * len(failed) / len(event_ids)
        logging.info(
            'Ran on %s ids, %s(%s) passed, %s(%s) failed', len(event_ids), int(passed_fraction * 100), len(passed),
            int(failed_fraction * 100), len(failed)
        )
        for event_id in passed:
            data = self._run_event(event_id)
            logging.warning('Event unexpectedly passed: %s: %s', event_id, '\n'.join(data[1]))

        self.assertTrue(fraction <= failed_fraction, 'Too many events passed: %s of %s' % (len(passed), len(event_ids)))
