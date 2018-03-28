# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    'd\.?c\.? swing',
    connected(Any('d\.?c\.? hand'), dance_keywords.EASY_DANCE),
    connected(Any('hand'), dance_keywords.EASY_DANCE),
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    SUPER_STRONG_KEYWORDS = REAL_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'DC_HAND'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'dc hand dancing',
            'hand dancing',
            'dc swing',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return []

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES + ['event']

    @classmethod
    def _get_classifier(cls):
        return Classifier
