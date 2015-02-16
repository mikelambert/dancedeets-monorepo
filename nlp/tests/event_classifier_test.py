# -*-*- encoding: utf-8 -*-*-
# was building this unittest so we can build a word-nearby-ness classifier to improve the qualify of classification.

import unittest

from nlp import event_classifier


class TestSoulSessionsOslo(unittest.TestCase):
    def runTest(self):
        fb_event = dict(info=dict(name="FB Event", description="sessions jam battles cyphers dj's"))
        classified_event = event_classifier.get_classified_event(fb_event)
        self.assertEqual(set([]), classified_event.dance_matches())
        self.assertEqual(set(['sessions', 'jam', 'battles', 'cyphers']), classified_event.event_matches())

class TestDanceClass(unittest.TestCase):
    def runTest(self):
        fb_event = dict(info=dict(name="FB Event", description="more stuff here with dance class"))
        classified_event = event_classifier.get_classified_event(fb_event)
        self.assertEqual(set(['dance']), classified_event.dance_matches())
        self.assertEqual(set(['class']), classified_event.event_matches())

class TestKeywordLoader(unittest.TestCase):
    def runTest(self):
        result = event_classifier._parse_keywords(['a', 'b#c', 'c  #d', 'd\\e', 'e\\#f', 'f\\##g'])
        self.assertEqual(result[event_classifier.INDEPENDENT_KEYWORD], ['a', 'b', 'c', 'd\\e', 'e\\#f', 'f\\#'])

        result = event_classifier._parse_keywords(['abcdefghijklmnopqrstuvwxyz#', 'ab(cd)ef #()', 'ab\(cd\)ef ###'])
        self.assertEqual(result[event_classifier.INDEPENDENT_KEYWORD], ['abcdefghijklmnopqrstuvwxyz', 'ab(cd)ef', 'ab\(cd\)ef'])

class TestCJK(unittest.TestCase):
    def runTest(self):
        fb_event = dict(info=dict(name="Blah", description="""
╔════════════════════════════╗

•´´¯`••. .•´´¯`••
lockdanceevent
╚════════════════════════════╝
•´´¯`••. •´´¯`••.
█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█
►
"""))
        classified_event = event_classifier.get_classified_event(fb_event)
        self.assertFalse(classified_event.is_dance_event())

if __name__ == '__main__':
    print unittest.main()
