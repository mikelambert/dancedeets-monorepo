# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.contact import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestContact(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_contact_improv_event)

    def runTest(self):
        self.assertEvents(
            0.95, [
                '188518311900331',
                '331758814010931',
                '185298802076147',
                '1492518260866433',
                '150736305588036',
                '413793102413606',
                '444726045943964',
                '131448867539689',
                '737814049757013',
                '398406093928333',
                '2292803707612602',
                '164103827559588',
                '1049377308423482',
                '817583831758075',
                '2016172295291444',
                '1045494882257047',
                '220942335119690',
                '152522918779248',
                '808223029385602',
                '270890010104938',
                '418908665172646',
                '1902062276775002',
                '1796341603999669',
                '744728512387350',
                '331758814010931',
            ]
        )


class TestNotContact(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_contact_improv_event)

    def runTest(self):
        self.assertNotEvents(1.0, [])


if __name__ == '__main__':
    print unittest.main()
