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
    GOOD_DANCE = keywords.STYLE_BREAK
    GOOD_BAD_PAIRINGS = [(keywords.STYLE_BREAK, keywords.WRONG_BREAK)]


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BREAKING'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'bboys',
            'bboying',
            'bgirl',
            'bgirls',
            'bgirling',
            'breakdancing',
            'breakdancers',
            'breakdanse',
            'footwork',
            'toprock',
            'power moves',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'bboy',
            'breaking',
            'breakdance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.STREET_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
