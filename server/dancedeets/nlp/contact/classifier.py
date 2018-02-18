# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

CONTACT = '[ck]onta[ck]t\w*'
IMPROV = 'improv\w*'

REAL_DANCE = Any(
    '%s\W?%s' % (CONTACT, IMPROV),
    commutative_connected(Any(IMPROV), Any(CONTACT)),
    u'接触即興',  # japanese
    u'即興接觸',  # chinese
    u'接觸即興',  # chinese
)

AMBIGUOUS_DANCE = Any(CONTACT)

KEYWORDS = Any(
    'connection'
    'weight',
    'momentum',
    'movement',
    'mover',
)


class ContactClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.COUNTRY

    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'jam',
        'lab',
        'festival',
    )

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(ContactClassifier, self).is_dance_event()
        if result:
            return result

        return False


def is_contact_improv_event(classified_event):
    classifier = ContactClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
