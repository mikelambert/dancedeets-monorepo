# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import partner

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    'disco\W?fox\w*',
    'disco\W?hustle',
    'swing\W?fox',
    u'дискофокс',
    'disco\W?swing',
    'rock\W?fox',
)

AMBIGUOUS_DANCE = Any(u'Хастл',)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'DISCOFOX'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'discofox',
            'disco hustle',
            'swing fox',
            'disco swing',
            'rock fox',
            u'Хастл',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_DANCE, REAL_DANCE)
