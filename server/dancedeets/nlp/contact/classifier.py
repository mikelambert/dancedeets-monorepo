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
IMPROV = 'impro[wv]\w*'

REAL_DANCE = Any(
    '%s\W?%s' % (CONTACT, IMPROV),
    commutative_connected(Any(IMPROV), Any(CONTACT)),
    u'接触即興',  # japanese
    u'即興接觸',  # chinese
    u'接觸即興',  # chinese
)

AMBIGUOUS_CONTACT = Name('AMBIGUOUS_CONTACT', Any(
    CONTACT,
    '[ck]i',
    '[ck]\W?i\W?',
))

KEYWORDS = Name(
    'KEYWORDS', Any(
        'contact'
        'connection'
        'weight',
        'momentum',
        'movement',
        'mover',
        'trust',
        'balance',
        'support',
        'bodies',
        'body',
    )
)


class ContactClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.CONTACT

    GOOD_DANCE = REAL_DANCE
    # Too many false positives
    # AMBIGUOUS_DANCE = AMBIGUOUS_CONTACT
    ADDITIONAL_EVENT_TYPE = Any(
        'jam',
        u'dżemów',
        'lab',
        'festival',
    )

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(ContactClassifier, self).is_dance_event()
        if result:
            return result

        result = self.is_ci_dance()
        if result:
            return result

        return False

    def is_ci_dance(self):
        title_is_ambiguous = self._title_has(AMBIGUOUS_CONTACT)
        has_contact_improv = self._has(self.GOOD_DANCE_FULL)
        num_keywords = len(set(self._get(KEYWORDS))) + len(set(self._get(keywords.EASY_DANCE)))
        if title_is_ambiguous and has_contact_improv:
            return 'title has CI/contact, body has contact improv'

        if title_is_ambiguous and num_keywords >= 2:
            return 'title has CI/contact, body has relevant bits'

        return False


def is_contact_improv_event(classified_event):
    classifier = ContactClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
