# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import aerial
from dancedeets.nlp.styles import pole

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
    pole.DANCE,
)

AERIALS = Any(
    u'aerials?',
    u'אריאלס',  # hebrew aerials
    u'空中',
)

AMBIGUOUS_DANCE = Any(
    pole.AMBIGUOUS_DANCE,
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
    GOOD_DANCE = Any(aerial.Classifier.GOOD_DANCE, pole.Classifier.GOOD_DANCE)
    AMBIGUOUS_DANCE = Any(aerial.Classifier.AMBIGUOUS_DANCE, pole.Classifier.AMBIGUOUS_DANCE)
    ADDITIONAL_EVENT_TYPE = Any(aerial.Classifier.ADDITIONAL_EVENT_TYPE, pole.Classifier.ADDITIONAL_EVENT_TYPE)
    GOOD_BAD_PAIRINGS = aerial.Classifier.GOOD_BAD_PAIRINGS + pole.Classifier.GOOD_BAD_PAIRINGS

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
        return []

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
