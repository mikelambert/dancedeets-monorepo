# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp.contact import classifier
from dancedeets.test_utils import unittest
from dancedeets.test_utils import classifier_util


class TestContact(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_contact_improv_event)

    def runTest(self):
        self.assertEvents(
            0.96, [
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
                '165250377560917',
                '408844392907915',
                '1998943853678300',
                '1924866001099177',
                '333489140473013',
                '163482180969963',
                '1717239484982398',
                '163692737569115',
                '2007890929468879',
                '550993618600306',
                '154344305198280',
                '219619141938956',
                '153626071877993',
                '1998943853678300',
            ]
        )


class TestNotContact(classifier_util.TestClassifier):
    classifier_func = staticmethod(classifier.is_contact_improv_event)

    def runTest(self):
        self.assertNotEvents(
            1.0,
            [
                '343280622823619',
                '336606790080595',
                '191827318217821',
                '1237530229726081',
                # wejściówka was matching 'ci' on non-unicode regexes
                '462115054126197',
                # wejściówka was matching 'ci' on non-unicode regexes
                '327973137673346',
                # świadomości was matching 'ci' on non-unicode regexes
                '283417325509347',
            ]
        )


if __name__ == '__main__':
    print unittest.main()
