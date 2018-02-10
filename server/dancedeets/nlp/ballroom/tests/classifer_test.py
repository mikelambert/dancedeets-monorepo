# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.latin import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestFoodSalsa(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_salsa_event)

    def runTest(self):
        self.assertNotEvent('1837327442944312')


class TestLatinCompetition(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_salsa_event)

    def runTest(self):
        self.assertEvent('151555808837731')
        self.assertEvent('1821516191478841')
        self.assertEvent('235945840191010')
        self.assertEvent('2092023671075343')
        self.assertEvent('1553984067995241')
        self.assertEvent('1422208217907436')
        self.assertEvent('344249636077753')
        self.assertEvent('165088020802863')


class TestLatinClass(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_salsa_event)

    def runTest(self):
        self.assertEvent('154418185279514')
        self.assertEvent('176239869784234')
        self.assertEvent('141598903209252')
        self.assertEvent('1801249549949792')
        self.assertEvent('1819024858358233')
        self.assertEvent('192105941525864')
        self.assertEvent('958189144215292')
        self.assertEvent('313780035693230')
        self.assertEvent('10153148050940861')


# Salsa intermedia performance group
# self.assertEvent('710368129168209')
# dance contest, with salsa/bachata keywords
#        self.assertEvent('1765036530470368')

if __name__ == '__main__':
    print unittest.main()
