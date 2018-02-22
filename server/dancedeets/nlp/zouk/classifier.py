# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
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
    'brazilian\w?zouk',
    'traditional zouk',
    'lambda\W?zouk',
    'modern\W?zouk',
    'mzouk',
    'soul\W?zouk',
    'zouk\W?fusion',
)

ZOUK = Any('zouk', u'ズウォーク', '\w{,7}zouk')
AMBIGUOUS_WORDS = Any(ZOUK)


class ZoukClassifier(base_auto_classifier.DanceStyleEventClassifier):
    __metaclass__ = base_auto_classifier.AutoRuleGenerator

    vertical = event_types.VERTICALS.ZOUK

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

        result = super(ZoukClassifier, self).is_dance_event()
        if result:
            return result

        return False

    @base_auto_classifier.log_to_bucket('is_zouk')
    def is_zouk(self):
        if self._title_has(ZOUK):
            return 'has zouk title'

        return False


def is_zouk_dance(classified_event):
    classifier = ZoukClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
