# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    'ragga\W?jamm?',
    u'댄스 ?레게',  # korean reggae dance
    u'레게 ?댄스',  # korean reggae dance
    u'דאנסהול',  # hebrew dancehall
)

AMBIGUOUS_DANCE = Any(
    'dancehall',
    u'ダンスホール',
    u'댄스홀',
    'reggae',
    u'レゲエ',
    u'레게',
    'reggaeton',
    u'レゲトン',
    u'레게 ?톤',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    REAL_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'DANCEHALL'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'ダンスホール',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'dancehall',
            'ragga jam',
            'reggae',
            'reggaeton',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(REAL_DANCE, AMBIGUOUS_DANCE)
