# -*-*- encoding: utf-8 -*-*-

import logging
import os
from dancedeets import fb_api
from dancedeets.nlp import event_classifier
from dancedeets.nlp import styles
from dancedeets.nlp.styles import street
from dancedeets.nlp.styles.tests import util
from dancedeets.test_utils import classifier_util
from dancedeets.test_utils import unittest

TEST_IDS_PATH = util.TEST_IDS_PATH


def get_positive_negative_ids(style_name):
    positives = {}
    negatives = {}

    for filename in os.listdir(TEST_IDS_PATH):
        if filename != '%s.txt' % style_name:
            continue
        full_path = os.path.join(TEST_IDS_PATH, filename)
        for line in open(full_path).readlines():
            try:
                line = line.split('#')[0].strip()
                if not line:
                    continue
                try:
                    classification, event_id = line.split(':', 1)
                except:
                    logging.exception('Error on line: %r', line)
                if classification.startswith('-'):
                    lookup = negatives
                    key = classification[1:]
                else:
                    lookup = positives
                    key = classification
                if key not in lookup:
                    lookup[key] = set()
                lookup[key].add(event_id)
            except:
                logging.exception('Error processing line: %s', line)
                raise
    return positives, negatives


def get_classified_event(fb_event, style_name):
    street_name = street.Style.get_name()
    if style_name == street_name:
        classifier_type = event_classifier.ClassifiedEvent
    else:
        classifier_type = event_classifier.BasicClassifiedEvent

    classified_event = event_classifier.get_classified_event(fb_event, classifier_type=classifier_type)
    return classified_event


def get_false_positives_and_negatives(positives, negatives, get_event):
    # Quick test, verify we have classifiers for everything
    for style_name in positives:
        assert styles.CLASSIFIERS[style_name]

    false_negatives = {}
    false_positives = {}
    for style_name, event_ids in positives.iteritems():
        classifier_class = styles.CLASSIFIERS[style_name]
        for event_id in event_ids:
            fb_event = get_event(event_id)
            classified_event = get_classified_event(fb_event, style_name)
            classifier = classifier_class(classified_event)
            is_dance_event = classifier.is_dance_event()
            if not is_dance_event:
                logging.warning('Event unexpectedly failed: %s: %s', event_id, '\n'.join(classifier.debug_info()))
                false_negatives.setdefault(style_name, []).append(event_id)

    for style_name, event_ids in negatives.iteritems():
        classifier_class = styles.CLASSIFIERS[style_name]
        for event_id in event_ids:
            fb_event = get_event(event_id)
            classified_event = get_classified_event(fb_event, style_name)
            classifier = classifier_class(classified_event)
            is_dance_event = classifier.is_dance_event()
            if is_dance_event:
                logging.warning('Event unexpectedly passed: %s: %s', event_id, '\n'.join(classifier.debug_info()))
                false_positives.setdefault(style_name, []).append(event_id)

    return false_positives, false_negatives


def print_stats(positives, negatives, false_positives, false_negatives, get_event):
    positive_count = sum(len(x) for x in positives.values())
    negative_count = sum(len(x) for x in negatives.values())
    false_positive_count = sum(len(x) for x in false_positives.values())
    false_negative_count = sum(len(x) for x in false_negatives.values())

    if negative_count:
        false_positive_rate = 1.0 * false_positive_count / negative_count
        print 'FP %s: %2.f%%' % (false_positive_count, 100 * false_positive_rate)

    if positive_count:
        false_negative_rate = 1.0 * false_negative_count / positive_count if positive_count else 'N/A'
        print 'FN %s: %2.f%%' % (false_negative_count, 100 * false_negative_rate)

    for style_name, event_ids in false_negatives.iteritems():
        for event_id in event_ids:
            event = get_event(event_id)
            print 'FN-%s: %s: %s' % (style_name, event_id, event['info']['name'])

    for style_name, event_ids in false_positives.iteritems():
        for event_id in event_ids:
            event = get_event(event_id)
            print 'FP-%s: %s: %s' % (style_name, event_id, event['info']['name'])


def get_event_data(fbl, ids):
    ids = list(ids)
    return dict((id, event) for (id, event) in zip(ids, fbl.get_multi(fb_api.LookupEvent, ids)))


def get_ids(positives, negatives):
    all_ids = set()
    for event_ids in positives.values():
        all_ids.update(event_ids)
    for event_ids in negatives.values():
        all_ids.update(event_ids)
    return all_ids


class TestFiles(classifier_util.TestClassifier):
    cache_db_path = util.CACHE_PATH

    def runTest(self):
        style_name = os.environ.get('EXTRA_ARGS')
        positives, negatives = get_positive_negative_ids(style_name)
        all_ids = get_ids(positives, negatives)
        event_data = get_event_data(self.fbl, all_ids)
        get_event = lambda x: event_data[x]
        false_positives, false_negatives = get_false_positives_and_negatives(positives, negatives, get_event)
        print_stats(positives, negatives, false_positives, false_negatives, get_event)


if __name__ == '__main__':
    print unittest.main()
