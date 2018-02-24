# -*-*- encoding: utf-8 -*-*-

import logging
import os
from dancedeets.nlp import event_classifier
from dancedeets.nlp import styles
from dancedeets.test_utils import classifier_util
from dancedeets.test_utils import unittest

GOOD_IDS = []

BAD_IDS = []

TEST_IDS_PATH = os.path.join(os.path.dirname(styles.__file__), 'test_ids')


class TestFiles(classifier_util.TestClassifier):
    def runTest(self):

        positive = {}
        negative = {}

        for filename in os.listdir(TEST_IDS_PATH):
            full_path = os.path.join(TEST_IDS_PATH, filename)
            for line in open(full_path).readlines():
                line = line.split('#')[0].strip()
                if not line:
                    continue
                classification, event_id = line.split(':')
                if classification.startswith('-'):
                    lookup = negative
                    key = classification[1:]
                else:
                    lookup = positive
                    key = classification
                if key not in lookup:
                    lookup[key] = set()
                lookup[key].add(event_id)

        false_negatives = []
        false_positives = []
        positive_count = 0
        negative_count = 0
        for style_name, event_ids in positive.iteritems():
            classifier_class = styles.CLASSIFIERS[style_name]
            for event_id in event_ids:
                positive_count += 1
                fb_event = self.get_event(event_id)
                classified_event = event_classifier.get_classified_event(fb_event)
                classifier = classifier_class(classified_event)
                is_dance_event = classifier.is_dance_event()
                if not is_dance_event:
                    logging.warning('Event unexpectedly failed: %s: %s', event_id, '\n'.join(classifier.debug_info()))
                    false_negatives.append(event_id)

        for style_name, event_ids in negative.iteritems():
            classifier_class = styles.CLASSIFIERS[style_name]
            for event_id in event_ids:
                negative_count += 1
                fb_event = self.get_event(event_id)
                classified_event = event_classifier.get_classified_event(fb_event)
                classifier = classifier_class(classified_event)
                is_dance_event = classifier.is_dance_event()
                if is_dance_event:
                    logging.warning('Event unexpectedly passed: %s: %s', event_id, '\n'.join(classifier.debug_info()))
                    false_positives.append(event_id)

        false_positive_rate = 1.0 * len(false_positives) / negative_count
        false_negative_rate = 1.0 * len(false_negatives) / positive_count

        print 'FP %s: %2.f%%' % (len(false_positives), 100 * false_positive_rate)
        print 'FN %s: %2.f%%' % (len(false_negatives), 100 * false_negative_rate)

        for event_id in false_negatives:
            event = self.get_event(event_id)
            print 'FN: %s: %s' % (event_id, event['info']['name'])

        for event_id in false_positives:
            event = self.get_event(event_id)
            print 'FP: %s: %s' % (event_id, event['info']['name'])


if __name__ == '__main__':
    print unittest.main()
