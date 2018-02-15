# -*-*- encoding: utf-8 -*-*-

from dancedeets import fb_api
from dancedeets.nlp import event_classifier
from dancedeets.nlp.street import classifier
from dancedeets.nlp.street import rules
from dancedeets.test_utils import classifier_util
from dancedeets.test_utils import unittest


class TestSimpleMatches(unittest.TestCase):
    def runTest(self):
        self.assertTrue(rules.GOOD_DANCE.hack_double_regex()[1].findall('streetdance'))


class TestClassifier(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_street_event)

    def runTest(self):
        self.assertEvents(1.0, [
            '292568747504427',
            '113756888764413',
            '127125550747109',
        ])


class TestNotClassifier(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_street_event)

    def runTest(self):
        self.assertNotEvents(
            1.0,
            [
                '101883956566382',
                '194555360659913',
                '149083330948',
                '170007276417905',
                # main stacks voting...that points at a 'dancecontest'
                # '278853778841357',
            ]
        )


# shoudld be breakdance event
# '114633285919267'

if __name__ == '__main__':
    print unittest.main()
