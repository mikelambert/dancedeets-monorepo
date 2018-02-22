# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.soulline import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util

FUNC = classifier.is_line_event

GOOD_IDS = []

BAD_IDS = []


class TestSoulLine(classifier_util.TestClassifier):
    classifier_func = staticmethod(FUNC)

    def runTest(self):
        self.assertEvents(0.95, GOOD_IDS)


class TestNotSoulLine(classifier_util.TestClassifier):
    classifier_func = staticmethod(FUNC)

    def runTest(self):
        self.assertNotEvents(1.0, BAD_IDS)


if __name__ == '__main__':
    print unittest.main()
