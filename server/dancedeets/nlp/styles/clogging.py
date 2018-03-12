# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

SUPER_STRONG_KEYWORDS = Any(
    'america\'s clogging hall of fame',
    'clogging champions of america',
    'america onstage',
)

AMBIGUOUS_DANCE = Any(u'clog')

CLOGGING = Any(
    u'clogging',
    u'cloggers?',
    commutative_connected(Any(u'clog'), dance_keywords.EASY_DANCE),
)
GOOD_DANCE = CLOGGING


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    SUPER_STRONG_KEYWORDS = SUPER_STRONG_KEYWORDS

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'CLOGGING'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [u'clogging', u'clog dance']

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
