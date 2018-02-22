# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

DANCE = Any(
    'pole\W?ates',
    'aerial\Whoop',
    'aerial\Wfabric',
)
AMBIGUOUS_DANCE = Any(
    'pole',
    'aerials?',
    'hoops?',
    'fabrics?',
    'silks?',
)
EVENT_TYPES = Any(
    'miss',  # miss pole dance
    'series',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = 'AERIAL_POLE'

    GOOD_DANCE = DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    EVENT_TYPES = EVENT_TYPES

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'AERIAL_POLE'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'pole dance',
            'aerial hoop',
            'aerial fabric',
            'hoop dance',
            'pole',
            'slik dance',
            'pole-ates',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return [
            'series',
        ]

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        raise Any(DANCE, AMBIGUOUS_DANCE)
