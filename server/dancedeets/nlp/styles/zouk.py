# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import partner
from ..ballroom import classifier as ballroom_classifier
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    u'ズーク',
    'zouk\w+',  # not just plain zouk
    'zouk\W?lambada',
    'brazilian\W?zouk',
    'traditional zouk',
    'lambda\W?zouk',
    'modern\W?zouk',
    'mzouk',
    'soul\W?zouk',
    'zouk\W?fusion',
)

ZOUK = Any('zouk', u'ズウォーク', '\w{,7}zouk')
AMBIGUOUS_WORDS = Any(ZOUK)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):

    AMBIGUOUS_DANCE = AMBIGUOUS_WORDS
    GOOD_DANCE = REAL_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'meeting',
        'incontro',
        'festival',
        'marathon',
        'social',
    )
    GOOD_BAD_PAIRINGS = [
        (Any(u'ズーク'), Any('zook', u'バイク', 'zouk club', 'club zouk')),
    ]

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = self.is_zouk()
        if result:
            return result

        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        return False

    @base_auto_classifier.log_to_bucket('is_zouk')
    def is_zouk(self):
        if self._title_has(ZOUK):
            return 'has zouk title'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'ZOUK'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'zouk',
            'brazilian zouk',
            'zouk lambada',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_WORDS, REAL_DANCE)
