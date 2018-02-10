# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.latin import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestFoodSalsa(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_salsa_event)

    def runTest(self):
        for event_id in [
            '597069203796616',
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
            '448420245336858',
            '1917059178551409',
            '505865189813278',
            '119912795431444',
        ]:
            self.assertEvent(event_id)


if __name__ == '__main__':
    print unittest.main()
