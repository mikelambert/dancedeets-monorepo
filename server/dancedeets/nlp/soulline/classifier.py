# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

LINE_DANCE = Any(
    'soul\W?line\w*',
    'r\W+b\Wline?\Wdanc\w*',
    '(?:baltimore|b\W?more|chicago|chi\W?town)? line\W?danc\w*',
    'chitown slide',
    'urban\W?line\W?danc\w*',
    'cleveland shuffle',
    'wobble line\w*',
    'zydeco line\w*',
)


class SoulLineClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.SOULLINE

    GOOD_DANCE = LINE_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'convention',
        'marathon',
        'brunch',
        'throwdown',
        'party',
    )

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(SoulLineClassifier, self).is_dance_event()
        if result:
            return result

        return False


def is_line_event(classified_event):
    classifier = SoulLineClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
