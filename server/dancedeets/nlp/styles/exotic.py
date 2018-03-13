# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

GOOD_DANCE = commutative_connected(Any(
    'chair',
    'lap',
    'exotic',
    'strip',
    'go\W?go',
), dance_keywords.EASY_DANCE)
AMBIGUOUS_DANCE = Any(
    'lap',
    # Should we do a separate 'heels' category?
    # Was accidentally triggering a country/western 'kick up your heels'
    #'heels',
    'exotic',
    'flirt',
    'sexy',
    'strip\W?tease',
    u'стрипластика',  # strip-plastic (strip dancing?)
)
EVENT_TYPES = Any(
    'miss',  # miss pole dance
    'series',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    EVENT_TYPES = EVENT_TYPES
    GOOD_BAD_PAIRINGS = [
        (Any('lap'), Any('race')),
    ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'EXOTIC'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'lap dance',
            'heels dance',
            'chair dance',
            'flirt dance',
            'pole dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return [
            'series',
        ]

    @classmethod
    def _get_classifier(cls):
        return Classifier
