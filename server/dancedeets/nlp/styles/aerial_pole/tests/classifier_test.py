# -*-*- encoding: utf-8 -*-*-

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
                classification, event_id = line.strip().split(':')
                if classification.startswith('-'):
                    lookup = negative
                    key = classification[1:]
                else:
                    lookup = positive
                    key = classification
                if key not in lookup:
                    lookup[key] = set()
                lookup[key].add(event_id)

        false_negatives = set()
        false_positives = set()
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
                    false_negatives.add(event_id)

        for style_name, event_ids in negative.iteritems():
            classifier_class = styles.CLASSIFIERS[style_name]
            for event_id in event_ids:
                negative_count += 1
                fb_event = self.get_event(event_id)
                classified_event = event_classifier.get_classified_event(fb_event)
                classifier = classifier_class(classified_event)
                is_dance_event = classifier.is_dance_event()
                if is_dance_event:
                    false_positives.add(event_id)

        false_positive_rate = 1.0 * len(false_positives) / positive_count
        false_negative_rate = 1.0 * len(false_negatives) / negative_count

        print false_positive_rate
        print false_negative_rate


if __name__ == '__main__':
    print unittest.main()
