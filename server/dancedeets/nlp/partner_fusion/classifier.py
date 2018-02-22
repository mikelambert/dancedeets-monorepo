# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any('modern jive', 'ceroc', 'leroc', 'le-roc')

FUSION = Any(
    'fusion',
    u'fusión?',
)

BLUES = Any('blues')

AMBIGUOUS_DANCE = Any(
    BLUES,
    commutative_connected(BLUES, FUSION),
    commutative_connected(FUSION, keywords.DANCE),
)


class FusionClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.PARTNER_FUSION

    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(FusionClassifier, self).is_dance_event()
        if result:
            return result

        return False


def is_fusion_event(classified_event):
    classifier = FusionClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
