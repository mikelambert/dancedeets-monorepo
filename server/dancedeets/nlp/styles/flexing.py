# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import event_types
from dancedeets.nlp.street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = keywords.STYLE_FLEX
    GOOD_BAD_PAIRINGS = [
        (keywords.STYLE_FLEX, keywords.WRONG_FLEX),
    ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'FLEXING'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'flexing dance',
            'flex dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.STREET_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
