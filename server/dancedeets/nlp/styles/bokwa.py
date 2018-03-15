# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any('bokwa',)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    SUPER_STRONG_KEYWORDS = REAL_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BOKWA'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'bokwa',
            'bokwa step',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
