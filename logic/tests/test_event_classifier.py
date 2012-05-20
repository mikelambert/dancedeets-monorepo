# -*-*- encoding: utf-8 -*-*-
# was building this unittest so we can build a word-nearby-ness classifier to improve the qualify of classification.

import unittest

from logic import event_classifier


class TestClassifier(unittest.TestCase):
    def test_SoulSessionsOslo(self):
        fb_event = dict(info=dict(name="FB Event", description="sessions jam battles cyphers dj's"))
        classified_event = event_classifier.get_classified_event(fb_event)
        self.assertEqual(set([]), classified_event.dance_matches())
        self.assertEqual(set(['sessions', 'jam', 'battles', 'cyphers']), classified_event.event_matches())
    def test_DanceClass(self):
        fb_event = dict(info=dict(name="FB Event", description="more stuff here with dance class"))
        classified_event = event_classifier.get_classified_event(fb_event)
        self.assertEqual(set(['dance']), classified_event.dance_matches())
        self.assertEqual(set(['class']), classified_event.event_matches())

    def test_CJK(self):
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
