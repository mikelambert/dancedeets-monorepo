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

ARGENTINE = Any(
    'argentin\w+',
    u'アルゼンチン',
    u'阿根廷',
    u'아르헨티나',
)

TANGO = Any(
    'tango',
    u'タンゴ',
    u'探戈',
    u'탱고',
)
TANGO_TYPES = Any(
    'traditional',
    'nuevo',
    u'ヌオーバ',
    u'새로운',
    'milonga',
    u'ミロンガ',
    u'밀롱가',
    'vals',
    u'バルス',
    u'왈츠',
    'alternative',
)
REAL_DANCE = commutative_connected(ARGENTINE, TANGO)

AMBIGUOUS_WORDS = Any(
    TANGO_TYPES,
    TANGO,
    commutative_connected(TANGO_TYPES, TANGO),
)

EXTRAS = Any(ARGENTINE, TANGO_TYPES, keywords.EASY_DANCE)


class TangoClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.TANGO

    AMBIGUOUS_DANCE = AMBIGUOUS_WORDS
    GOOD_DANCE = REAL_DANCE
    ADDITIONAL_EVENT_TYPE = Any('meeting', 'incontro', 'festival', 'marathon', 'milongas?')
    BAD_DANCE = None
    GOOD_BAD_PAIRINGS = [
        (TANGO, Any('whiskey tango')),
    ]

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(TangoClassifier, self).is_dance_event()
        if result:
            return result

        result = self.is_tango()
        if result:
            return result

        return False

    def is_tango(self):
        if self._title_has(TANGO) and len(list(self._get(EXTRAS))) >= 2:
            return 'has tango title and tango/dance keywords'

        return False


def is_tango_dance(classified_event):
    if ballroom_classifier.is_ballroom_event(classified_event)[0]:
        return (False, ['Ballroom event'], None)

    classifier = TangoClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
