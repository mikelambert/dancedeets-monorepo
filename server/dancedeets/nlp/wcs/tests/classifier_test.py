# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.wcs import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestWCS(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_wcs_event)

    def runTest(self):
        self.assertEvents(
            0.80,
            [
                # only teacher names
                '467976933581754',
                '182127055715910',
                # just instructors
                '993731020765760',
                # WCS not in title
                '1970534596495858',
                # just wcs in title, but no other clues
                '1655103394511761',
                '919274481570683',
                '1122884351182053',
                '142071959918293',
                '155467318548143',
                '2057504207803969',
                '533394547025961',
                '277219186140908',
                '1545090152254794',
                '2006108466325646',
                '137574390253952',
                '102025870622021',
                '1599999056723525',
                '321460875024481',
                '1626163317472281',
                '337819223318563',
                '1918755888408943',
                '1598521753543374',
                '127703317946669',
                '2180964752130224',
                '195255187714958',
            ]
        )


if __name__ == '__main__':
    print unittest.main()
