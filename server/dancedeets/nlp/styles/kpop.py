# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

KPOP = Any(
    'k\W?pop\w*',
    u'케이팝',  # korean kpop
    u'كي بوب',  # arabic kpop
)

EVENT_TYPES = Any('show',)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = KPOP
    ADDITIONAL_EVENT_TYPE = EVENT_TYPES

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'KPOP'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'kpop',
            u'케이팝',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return ['revue']

    @classmethod
    def _get_classifier(cls):
        return Classifier
