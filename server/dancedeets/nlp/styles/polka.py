# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

POLKA_KEYWORDS = [
    u'la polca',  # spanish
    u'polca',  # portuguese
    u'polka',
    u'полк',  # macedonian
    u'полька',  # russian
    u'פולקה',  # hebrew
    u'البولكا',  # arabic
    u'ポルカ',  # japanese
    u'波尔卡',  # chinese simplified
    u'波爾卡',  # chinese traditional
    u'폴카',  # korean
]
AMBIGUOUS_DANCE = Any(*POLKA_KEYWORDS)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'POLKA'

    @classmethod
    def get_rare_search_keywords(cls):
        return POLKA_KEYWORDS

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'polka',
            'polca',
            'polka dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_DANCE)
