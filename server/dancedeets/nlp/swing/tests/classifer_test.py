# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.swing import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestSwingDance(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_swing_event)

    def runTest(self):
        self.assertEvents(
            1.0, [
                '519492811755048',
                '460976420932784',
                '1965101180428342',
                '537675733276574',
                '1730462027199508',
                '288390884896693',
                '136501980360816',
                '239980933117412',
                '1820958151495719',
                '395244410898308',
                '1565762550147066',
                '1716559228403289',
                '137538773588963',
                '2435804639977124',
                '1505736622806668',
                '159866691306652',
                '524655034557876',
                '530686140648826',
                '1783960065239641',
                '119912795431444',
            ]
        )


class TestLindyHop(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_swing_event)

    def runTest(self):
        self.assertEvents(
            1.0, [
                '1918041211789895',
                '1659438694078105',
                '1566310336809842',
                '142109133265853',
                '665224390344728',
                '185398422216946',
                '340913629645434',
                '1741523099485782',
                '1997117073896045',
                '143295246283702',
                '2366423360249579',
                '345690255889925',
                '159308061520450',
                '124120538150413',
                '137729153572921',
                '1697615750295549',
                '1917059178551409',
            ]
        )


class TestWCS(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_swing_event)

    def runTest(self):
        self.assertEvents(
            1.0, [
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
