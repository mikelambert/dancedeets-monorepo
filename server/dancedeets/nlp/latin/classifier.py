# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import grammar
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_SALSA = Name(
    'LATIN_REAL_SALSA',
    Any(
        'salsa on1',
        'salsa on2',
        'cuban salsa',
        'salsa cuba\w+',
        'salsa styling',
        'salsa shine',
        'salsa\W?tanz',
        'lad(?:y|ies) styling|styling ladies',
        'shines ladies|ladies shines',
        'salser[oa]s?',
    )
)

SALSA = Any(
    'salsa',
    u'サルサ',
)

AMBIGUOUS_DANCE_MUSIC = Name(
    'LATIN_AMBIGUOUS_DANCE_MUSIC', Any(
        'chacha',
        'samba',
        u'サンバ',
        'bachata',
        u'バチャータ',
        'merengue',
        'rh?umba',
        'afro\W?[ck]uba\w+',
    )
)

FOOD = Any(
    'food',
    'tastings',
    'cinco de mayo',
)

GOOD_DANCE = commutative_connected(AMBIGUOUS_DANCE_MUSIC, keywords.EASY_DANCE)

good_battle = Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST)
GOOD_DANCE_BATTLE = Name('LATIN_GOOD_DANCE_BATTLE', commutative_connected(AMBIGUOUS_DANCE_MUSIC, good_battle))

SALSA_DANCE_BATTLE = Name('LATIN_SALSA_DANCE_BATTLE', commutative_connected(SALSA, good_battle))


def is_dance_event(classified_event):
    real_keywords = classified_event.processed_text.get_tokens(REAL_SALSA)
    if real_keywords:
        return (True, 'Found strong keywords: %s' % real_keywords, event_types.VERTICALS.LATIN)

    dance_keywords = classified_event.processed_text.get_tokens(GOOD_DANCE)
    if dance_keywords:
        return (True, 'Found strong dance keywords: %s' % dance_keywords, event_types.VERTICALS.LATIN)

    good_contest = classified_event.processed_text.get_tokens(GOOD_DANCE_BATTLE)
    if good_contest:
        return (True, 'Found dance contest: %s' % good_contest, event_types.VERTICALS.LATIN)

    salsa_contest = classified_event.processed_text.get_tokens(SALSA_DANCE_BATTLE)
    food_terms = classified_event.processed_text.get_tokens(FOOD)
    if salsa_contest and not food_terms:
        return (True, 'Found non-food salsa contest: %s' % salsa_contest, event_types.VERTICALS.LATIN)

    return (False, '', [])
