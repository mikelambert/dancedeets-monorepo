# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.african import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestContact(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_african_event)

    def runTest(self):
        self.assertEvents(0.96, [
            '146358896066104',
            '164670954307608',
            '122978271816563',
            '1780392182257519',
        ])


class TestNotContact(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_african_event)

    def runTest(self):
        self.assertNotEvents(1.0, [])


if __name__ == '__main__':
    print unittest.main()
