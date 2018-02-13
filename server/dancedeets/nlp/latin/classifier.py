# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..street import keywords
Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Name(
    'LATIN_REAL_DANCE',
    Any(
        'salsa on1',
        'salsa on2',
        'cuban salsa',
        'salsa cuba\w+',
        'salsa footwork',
        'salsa styling',
        'salsa shines?',
        'lad(?:y|ies) styling|styling ladies',
        'shines ladies|ladies shines',
        'salser[oa]s?',
        'bachatango',
        'bachata sensual',
        u'莎莎舞',  # chinese salsa dance
        u'恰恰舞',  # chinese cha cha dance
        u'倫巴舞',  # chinese rumba dance
    )
)

SALSA = Any(
    'salsa',
    u'サルサ',
)

AMBIGUOUS_DANCE_MUSIC = Name(
    'LATIN_AMBIGUOUS_DANCE_MUSIC',
    Any(
        'cha\W?cha',
        'cha\W?cha\W?cha',
        u'莎莎',  # chinese salsa dance
        u'恰恰恰',  # chinese cha cha dance
        u'倫巴',  # chinese rumba dance
        u'桑巴',  # chinese samba
        u'살사',  # korean salsa
        u'바차타',  # korean bachata
        u'차차차?',  # korean chacha
        u'메렝게',  # korean merenge
        u'륨바',  # korean rumba
        u'삼바',  # kroean samba
        'samba',
        u'samba no p[ée]',
        'samba de gafieira',
        'samba pagode',
        u'samba ax[ée]',
        'samba\W?rock',
        'samba de roda',
        u'サンバ',
        'bachata',
        u'バチャータ',
        'merengue',
        'rh?umba',
        'afro\W?[ck]uba\w+',
    )
)

ALL_LATIN_STYLES = Any(REAL_DANCE, SALSA, AMBIGUOUS_DANCE_MUSIC)

FOOD = Any(
    'food',
    'tastings',
    'cinco de mayo',
)

GOOD_DANCE = Any(REAL_DANCE, commutative_connected(AMBIGUOUS_DANCE_MUSIC, keywords.EASY_DANCE))
GOOD_BATTLE = Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST)
GOOD_DANCE_BATTLE = Name('LATIN_GOOD_DANCE_BATTLE', commutative_connected(AMBIGUOUS_DANCE_MUSIC, GOOD_BATTLE))

SALSA_DANCE_BATTLE = Name('LATIN_SALSA_DANCE_BATTLE', commutative_connected(SALSA, GOOD_BATTLE))

class_keywords = Any(keywords.CLASS, 'batch')

all_class = Any(class_keywords, commutative_connected(keywords.PERFORMANCE, class_keywords))

STYLE_CLASS = commutative_connected(ALL_LATIN_STYLES, all_class)


class LatinClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = 'latin'

    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE_MUSIC
    GOOD_DANCE = Any(REAL_DANCE, SALSA)
    BAD_DANCE = None
    GOOD_BAD_PAIRINGS = [(SALSA, FOOD)]


def is_salsa_event(classified_event):

    result = is_dance_event(classified_event)
    if result[0]:
        return result

    result = is_many_latin_styles(classified_event)
    if result[0]:
        return result

    result = is_dance_workshop(classified_event)
    if result[0]:
        return result

    result = is_dance_battle(classified_event)
    if result[0]:
        return result

    return result


def is_many_latin_styles(classified_event):
    all_keywords = classified_event.processed_text.get_tokens(ALL_LATIN_STYLES)
    if len(set(all_keywords)) >= 3:
        return (True, 'Found many latin keywords: %s' % all_keywords, event_types.VERTICALS.LATIN)

    return (False, '', [])


def is_dance_event(classified_event):
    dance_keywords = classified_event.processed_text.get_tokens(GOOD_DANCE)
    if dance_keywords:
        return (True, 'Found strong dance keywords: %s' % dance_keywords, event_types.VERTICALS.LATIN)

    return (False, '', [])


def is_dance_workshop(classified_event):
    dance_class = classified_event.processed_text.get_tokens(STYLE_CLASS)
    if dance_class:
        return (True, 'Found dance class: %s' % dance_class, event_types.VERTICALS.LATIN)

    return (False, '', [])


def is_dance_battle(classified_event):
    good_contest = classified_event.processed_text.get_tokens(GOOD_DANCE_BATTLE)
    if good_contest:
        return (True, 'Found dance contest: %s' % good_contest, event_types.VERTICALS.LATIN)

    salsa_contest = classified_event.processed_text.get_tokens(SALSA_DANCE_BATTLE)
    food_terms = classified_event.processed_text.get_tokens(FOOD)
    if salsa_contest and not food_terms:
        return (True, 'Found non-food salsa contest: %s' % salsa_contest, event_types.VERTICALS.LATIN)

    return (False, '', [])
