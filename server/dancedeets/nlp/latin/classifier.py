# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import grammar
from ..street.keywords import EASY_DANCE

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_SALSA = Name(
    'REAL_SALSA',
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
    )
)

AMBIGUOUS_DANCE_MUSIC = Name(
    'AMBIGUOUS_DANCE_MUSIC',
    Any(
        'salsa',
        u'サルサ',
        'chacha',
        'samba',
        u'サンバ',
        'bachata',
        u'バチャータ',
        'merengue',
        'salsa',
        'rh?umba',
        'afro\W?[ck]uba\w+',
    )
)

GOOD_DANCE = commutative_connected(AMBIGUOUS_DANCE_MUSIC, EASY_DANCE),


def is_dance_event(classified_event):
    real_keywords = classified_event.processed_text.get_tokens(REAL_SALSA)
    if real_keywords:
        return (True, 'Found strong keywords: %s' % real_keywords, event_types.VERTICALS.LATIN)

    dance_keywords = classified_event.processed_text.get_tokens(GOOD_DANCE)
    if dance_keywords:
        return (True, 'Found strong dance keywords: %s' % dance_keywords, event_types.VERTICALS.LATIN)

    return (False, '', [])
