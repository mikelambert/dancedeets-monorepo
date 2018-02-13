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
    'lindy\W?hop',
    'west coast swing',
    'east coast swing',
    'solo jazz',
    'solo charleston',
    'partner charleston',
    'carolina shag',
    'collegiate shag',
    'st\W? louis shag',
    'modern jive',
    'jitterbug',
    'slow drag',
    'balboa\w*',
)

AMBIGUOUS_WORDS = Any(
    'jive\w*',
    'swing\w*',
    'charleston',
    'shag',
    'wcs',
    'ecs',
)

WCS = Any('wcs')

WCS_BASICS = Any(
    'sugar push',
    'sugar tuck',
    'left side pass',
    'under arm',
    'whip',
)

AMBIGUOUS_DANCE_MUSIC = Any('blues',)

GOOD_DANCE = Any(REAL_DANCE, commutative_connected(Any(AMBIGUOUS_DANCE_MUSIC, AMBIGUOUS_WORDS), keywords.EASY_DANCE))
GOOD_BATTLE = Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST)
GOOD_DANCE_BATTLE = commutative_connected(Any(AMBIGUOUS_DANCE_MUSIC, AMBIGUOUS_WORDS), GOOD_BATTLE)

class_keywords = Any(keywords.CLASS)

all_class = Any(class_keywords, commutative_connected(keywords.PERFORMANCE, class_keywords))
STYLE_CLASS = commutative_connected(
    Any(REAL_DANCE, AMBIGUOUS_WORDS, commutative_connected(AMBIGUOUS_DANCE_MUSIC, keywords.EASY_DANCE)), all_class
)

ALL_SWING_STYLES = Any(REAL_DANCE, AMBIGUOUS_WORDS, AMBIGUOUS_DANCE_MUSIC)


class SwingClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.SWING

    AMBIGUOUS_DANCE = Any(AMBIGUOUS_WORDS, AMBIGUOUS_DANCE_MUSIC)
    GOOD_DANCE = REAL_DANCE
    BAD_DANCE = None

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(SwingClassifier, self).is_dance_event()
        if result:
            return result

        result = self.is_wcs()
        if result:
            return result

        return False

    def is_wcs(self):
        if self._has(WCS) and self._has(WCS_BASICS):
            return 'has wcs and wcs keywords'

        return False


def is_swing_event(classified_event):
    if ballroom_classifier.is_ballroom_event(classified_event)[0]:
        return (False, ['Ballroom event'], None)

    classifier = SwingClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
