# -*-*- encoding: utf-8 -*-*-
# was building this unittest so we can build a word-nearby-ness classifier to improve the qualify of classification.

import unittest

from dancedeets.nlp import all_styles
from dancedeets.nlp import event_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import grammar_matcher
from dancedeets.nlp.street import keywords
from dancedeets.nlp.street import rules


class TestSoulSessionsOslo(unittest.TestCase):
    def runTest(self):
        fb_event = dict(info=dict(name="FB Event", description="sessions jam battles cyphers dj's"))
        classified_event = event_classifier.get_classified_event(fb_event)
        self.assertEqual(set([]), classified_event.dance_matches())
        self.assertEqual(set(['jam', 'battles', 'cyphers']), classified_event.event_matches())


class RuleMatches(unittest.TestCase):
    def matchRule(self, rule, s):
        string_processor = grammar_matcher.StringProcessor(s)
        self.assertTrue(string_processor.get_tokens(rule))

    def notMatchRule(self, rule, s):
        string_processor = grammar_matcher.StringProcessor(s)
        self.assertFalse(string_processor.get_tokens(rule))

    def runTest(self):
        self.matchRule(keywords.CLASS, 'beginner breakdance')
        self.matchRule(keywords.CLASS, 'beginner')
        self.matchRule(keywords.EASY_DANCE, u'χορός')
        self.matchRule(keywords.EASY_DANCE, u'www.danceaholics.co.uk')
        self.matchRule(all_styles.DANCE_WRONG_STYLE, 'khaligi-belly')
        self.matchRule(rules.GOOD_DANCE, 'hiphop dance')
        self.notMatchRule(rules.GOOD_DANCE, 'hiphop.\ndance')
        #self.matchRule(rules., 'classic w/ mark oliver')
        self.notMatchRule(grammar.Any('[ck]\W?i\W?'), u'wej\u015bci\xf3wka!')

        # Ensure commutative_connected
        self.matchRule(rules.GOOD_DANCE, 'lock dance')
        self.matchRule(rules.GOOD_DANCE, 'lockdance')


class TestDanceClass(unittest.TestCase):
    def runTest(self):
        fb_event = dict(info=dict(name="FB Event", description="more stuff here, dance class"))
        classified_event = event_classifier.get_classified_event(fb_event)
        self.assertEqual(set(['dance']), classified_event.dance_matches())
        self.assertEqual(set(['class']), classified_event.event_matches())


class TestKeywordLoader(unittest.TestCase):
    def runTest(self):
        result = grammar.FileBackedKeyword._parse_keywords(['a', 'b#c', 'c  #d', 'd\\e', 'e\\#f', 'f\\##g'])
        self.assertEqual(result[0], ['a', 'b', 'c', 'd\\e', 'e\\#f', 'f\\#'])

        result = grammar.FileBackedKeyword._parse_keywords(['abcdefghijklmnopqrstuvwxyz#', 'ab(cd)ef #()', 'ab\(cd\)ef ###'])
        self.assertEqual(result[0], ['abcdefghijklmnopqrstuvwxyz', 'ab(cd)ef', 'ab\(cd\)ef'])


class TestCJKAndWordBreaks(unittest.TestCase):
    def runTest(self):
        string_processor = grammar_matcher.StringProcessor(u'the blocking dance')
        self.assertFalse(string_processor.get_tokens(keywords.STYLE_LOCK))

        string_processor = grammar_matcher.StringProcessor(u'the locking dance')
        self.assertTrue(string_processor.get_tokens(keywords.STYLE_LOCK))

        string_processor = grammar_matcher.StringProcessor(u'今日はblockingです')
        self.assertFalse(string_processor.get_tokens(keywords.STYLE_LOCK))

        string_processor = grammar_matcher.StringProcessor(u'今日はlockingです')
        self.assertTrue(string_processor.get_tokens(keywords.STYLE_LOCK))

        string_processor = grammar_matcher.StringProcessor(u'今日はロックイングです')
        self.assertTrue(string_processor.get_tokens(keywords.STYLE_LOCK))

        string_processor = grammar_matcher.StringProcessor(u'今日はブロックイングです')
        # Ideally we'd like this to return false,
        # but word segmentation is near-impossible with cjk (and japanese katakana phrases)
        self.assertTrue(string_processor.get_tokens(keywords.STYLE_LOCK))


if __name__ == '__main__':
    print unittest.main()
