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
    '(?:nyc?|new york)\W?hustl\w*',
    'latin hustl\w*',
    'new\W?style\W?hustl\w*',
    u'хастл',  # russian hustle
)

AMBIGUOUS_DANCE = Any(
    'hustle',
    'nsh',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    GOOD_BAD_PAIRINGS = [(
        Any('hustle'),
        Any(
            'dirt[^y\W]\w*',
            'dirt',
            'road\w*',
            'race\w*',
            'racing',
            '5k',
            '10k',
            'miles?',
            'networking',
            'side hustle',
            'walk\w+',  # avoid 'walk-in', but catch 'walking'
            'hustle bustle',
            'survive',
            'ddr',
        )
    )]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'HUSTLE'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'hustle',
            'new york hustle',
            'ny hustle',
            'latin hustle',
            'hustle dance',
            'nsh',
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
