# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

DANCE = Any(
    u'pole\W?ates',
    u'폴댄스',  # korean pole dance
    'pole\W?fit(?:ness)?',
)

AMBIGUOUS_DANCE = Any(
    'pole',
    u'ポール',
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
    ADDITIONAL_EVENT_TYPE = EVENT_TYPES
    GOOD_BAD_PAIRINGS = []

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'POLE'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'pole dance',
            'pole fitness',
            'pole fit',
            'pole',
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
