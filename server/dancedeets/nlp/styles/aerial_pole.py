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
    'aerial\Whoops?',
    'aerial\Wfabrics?',
    'aerial\Wsilks?',
    u'空中シルク',
    u'空中布',
    u'空中フープ',
)
AMBIGUOUS_DANCE = Any(
    'pole',
    u'ポール',
    'aerials?',
    u'空中',
    #'hoops?',
    'fabrics?',
    u'布',
    'silks?',
    u'シルク',
    'lyra',
)
EVENT_TYPES = Any(
    'miss',  # miss pole dance
    'series',
)

# Not currently used
RELATED_KEYWORDS = Any(
    'straddles?',
    'butterfl(?:y|ies)',
    'tricks',
    'tricksters?',
    'pole',
    'polers?',
    'climb',
    'aerial',
    'blackgirlspole',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
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
            'aerial silks',
            'hoop dance',
            'pole',
            'silk dance',
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
        return Any(DANCE, AMBIGUOUS_DANCE)
