# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.ballroom import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestBallroom(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_ballroom_event)

    def runTest(self):
        self.assertEvents(
            0.9, [
                '314224369066155',
                '394488887658045',
                '137419906955466',
                '1883229155325758',
                '1490262087724919',
                '241729456364219',
                '166178407473901',
                '328346594242548',
                '1487841387998564',
                '298460944016731',
                '2063158660376210',
                '167367140518143',
                '786669468197169',
                '1667505486635344',
                '184798295440137',
                '736502189887397',
            ]
        )


class TestNotBallroom(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_ballroom_event)

    def runTest(self):
        self.assertNotEvents([
            '1917059178551409',
            '505865189813278',
        ])


class TestNotBallroom(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_ballroom_event)

    def runTest(self):
        self.assertNotEvents(1.0, [
            '597069203796616',
            '119912795431444',
        ])


if __name__ == '__main__':
    print unittest.main()
