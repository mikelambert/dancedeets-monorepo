# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.latin import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestFoodSalsa(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_salsa_event)

    def runTest(self):
        self.assertNotEvent('1837327442944312')


class TestLatinCompetition(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_salsa_event2)

    def runTest(self):
        self.assertEvents(
            1.0, [
                '151555808837731',
                '1821516191478841',
                '235945840191010',
                '2092023671075343',
                '1553984067995241',
                '1422208217907436',
                '344249636077753',
                '165088020802863',
            ]
        )


class TestLatinClass(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_salsa_event2)

    def runTest(self):
        self.assertEvents(
            1.0, [
                '154418185279514',
                '176239869784234',
                '141598903209252',
                '1801249549949792',
                '1819024858358233',
                '192105941525864',
                '958189144215292',
                '313780035693230',
                '10153148050940861',
            ]
        )


# Salsa intermedia performance group
# self.assertEvent('710368129168209')
# dance contest, with salsa/bachata keywords
#        self.assertEvent('1765036530470368')

if __name__ == '__main__':
    print unittest.main()
