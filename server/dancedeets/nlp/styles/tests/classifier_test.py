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


def get_positive_negative_ids():
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

    return positive, negative


class TestFiles(classifier_util.TestClassifier):
    def runTest(self):
        positive, negative = get_positive_negative_ids()

        false_negatives = {}
        false_positives = {}
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
                    false_negatives.setdefault(style_name, []).append(event_id)

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
                    false_positives.setdefault(style_name, []).append(event_id)

        false_positive_count = sum(len(x) for x in false_positives.values())
        false_negative_count = sum(len(x) for x in false_negatives.values())

        false_positive_rate = 1.0 * false_positive_count / negative_count
        false_negative_rate = 1.0 * false_negative_count / positive_count

        print 'FP %s: %2.f%%' % (false_positive_count, 100 * false_positive_rate)
        print 'FN %s: %2.f%%' % (false_negative_count, 100 * false_negative_rate)

        for style_name, event_ids in false_negatives.iteritems():
            for event_id in event_ids:
                event = self.get_event(event_id)
                print 'FN-%s: %s: %s' % (style_name, event_id, event['info']['name'])

        for style_name, event_ids in false_positives.iteritems():
            for event_id in event_ids:
                event = self.get_event(event_id)
                print 'FP-%s: %s: %s' % (style_name, event_id, event['info']['name'])


if __name__ == '__main__':
    print unittest.main()
