# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.street import keywords
from dancedeets.nlp.styles import street

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected


class Classifier(street.StreetBaseClassifier):
    GOOD_DANCE = keywords.STYLE_HIPHOP
    AMBIGUOUS_DANCE = keywords.STYLE_HIPHOP_WEAK


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'HIPHOP'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'hiphop danse',
            'hip hop danse',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'streetjazz',
            'street jazz',
            'street-jazz',
            'hiphop',
            'hiphop dance',
            'hip hop',
            'hip hop dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.STREET_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
