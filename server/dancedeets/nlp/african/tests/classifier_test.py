# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.african import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestAfrican(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_african_event)

    def runTest(self):
        self.assertEvents(
            0.96, [
                '146358896066104',
                '164670954307608',
                '122978271816563',
                '1780392182257519',
                '145307596278281',
                '152086672237986',
                '473150429751553',
                '376687966118398',
                '152353025558570',
                '186737408729319',
                '1766568976984875',
                '2014008998837723',
                '1465864026844823',
                '143642779748400',
                '158023844978301',
                '130904450785969',
                '625677964290835',
                '760794604070401',
            ]
        )


class TestNotAfrican(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_african_event)

    def runTest(self):
        self.assertNotEvents(1.0, [])


if __name__ == '__main__':
    print unittest.main()
