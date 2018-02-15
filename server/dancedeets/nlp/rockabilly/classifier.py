# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    'jive\W?bop',
    'jive\W?freestyle',
    commutative_connected(Any('barn'), keywords.DANCE),
)

AMBIGUOUS_DANCE = Any(
    'jive',
    'boogie\W?woogie',
    'rock\W?\W?(?:n|and|&|\+)\W?\W?roll\w*',
    'rockabilly',
    'r\Wn\Wr',
    'boogie',
    'boogie\w*',
    u'ロッカビリー',
    u'ブギウギ',
)


class RockabillyClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.ROCKABILLY

    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'ball',
        u'バール',
        'festival',
        'marathon',
    )
    BAD_DANCE = Any('modern jive',)
    GOOD_BAD_PAIRINGS = [
        (Any('jive'), Any('modern jive')),
    ]

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(RockabillyClassifier, self).is_dance_event()
        if result:
            return result

        return False


def is_rockabilly_event(classified_event):
    classifier = RockabillyClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
