# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

KOMPA = Any(
    u'[ck]o[mn]pas?',
    u'компа',  # macedonian
)
AMBIGUOUS_DANCE = KOMPA


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'KOMPA'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'compa',
            'conpa',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'konpa',
            'konpa dance',
            'kompa',
            'kompa dance',
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
