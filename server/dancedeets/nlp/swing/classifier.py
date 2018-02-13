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
    'carolina shag',
    'collegiate shag',
    'st\W? louis shag',
    'modern jive',
    'jitterbug',
    'slow drag',
)

AMBIGUOUS_WORDS = Any(
    'jive\w*',
    'swing\w*',
    'balboa\w*',
    'charleston',
    'shag',
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


def is_swing_event(classified_event):
    if ballroom_classifier.is_ballroom_event(classified_event)[0]:
        return (False, ['Ballroom event'], [])

    classifier = SwingClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical

    result = is_dance_event(classified_event)
    if result[0]:
        return result

    result = is_many_swing_styles(classified_event)
    if result[0]:
        return result

    result = is_dance_workshop(classified_event)
    if result[0]:
        return result

    result = is_dance_battle(classified_event)
    if result[0]:
        return result

    return result


def is_many_swing_styles(classified_event):
    all_keywords = classified_event.processed_text.get_tokens(ALL_SWING_STYLES)
    if len(set(all_keywords)) >= 3:
        return (True, 'Found many swing keywords: %s' % all_keywords, event_types.VERTICALS.SWING)

    return (False, '', [])


def is_dance_event(classified_event):
    dance_keywords = classified_event.processed_text.get_tokens(GOOD_DANCE)
    if dance_keywords:
        return (True, 'Found strong dance keywords: %s' % dance_keywords, event_types.VERTICALS.SWING)

    return (False, '', [])


def is_dance_workshop(classified_event):
    dance_class = classified_event.processed_text.get_tokens(STYLE_CLASS)
    if dance_class:
        return (True, 'Found dance class: %s' % dance_class, event_types.VERTICALS.SWING)

    return (False, '', [])


def is_dance_battle(classified_event):
    good_contest = classified_event.processed_text.get_tokens(GOOD_DANCE_BATTLE)
    if good_contest:
        return (True, 'Found dance contest: %s' % good_contest, event_types.VERTICALS.SWING)

    return (False, '', [])
