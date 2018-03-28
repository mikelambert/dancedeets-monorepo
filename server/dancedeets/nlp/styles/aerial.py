# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import swing

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

DANCE = Any(
    u'aerial\Whoops?',
    u'aerial\Wfabrics?',
    u'aerial\Wsilks?',
    u'aerial\Wspirals?',
    u'aerial\W?tissues?',
    u'air equilibre',
    u'equilibre air',
    u'cerceau aérien',
    u'воздушн\w+ кольце',  # aerial hoop
    u'воздушн\w+ полотна\w*',  # aerial silks
    u'воздушн\w+ эквилибр',  # russian 'airborne equilibrium'
    u'空中シルク',
    u'空中布',
    u'空中フープ',
)

AERIALS = Any(
    u'aerials?',
    u'אריאלס',  # hebrew aerials
    u'空中',
)

AMBIGUOUS_DANCE = Any(
    AERIALS,
    #'hoops?',
    u'cerceaux?',
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


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = EVENT_TYPES
    GOOD_BAD_PAIRINGS = [
        # Don't include "lindy aerials"
        (AERIALS, swing.Style.get_cached_basic_regex()),
    ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'AERIAL'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'aerial hoop',
            'aerial fabric',
            'aerial silks',
            'hoop dance',
            'silk dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return [
            'series',
        ]

    @classmethod
    def _get_classifier(cls):
        return Classifier
