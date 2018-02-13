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

class_keywords = Any(keywords.CLASS, 'batch')
all_class = Any(class_keywords, commutative_connected(keywords.PERFORMANCE, class_keywords))


class LatinClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = 'latin'

    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE_MUSIC
    GOOD_DANCE = Any(REAL_DANCE, SALSA)
    BAD_DANCE = None
    GOOD_BAD_PAIRINGS = [(SALSA, FOOD)]

    def _quick_is_dance_event(self):
        return True


def is_salsa_event(classified_event):
    classifier = LatinClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info()
