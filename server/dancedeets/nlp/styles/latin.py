# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import partner

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

AMBIGUOUS_DANCE_MUSIC = Name(
    'LATIN_AMBIGUOUS_DANCE_MUSIC',
    Any(
        u'莎莎',  # chinese salsa dance
        u'살사',  # korean salsa
        'cha\W?cha',
        'cha\W?cha\W?cha',
        u'恰恰恰?',  # chinese cha cha dance
        u'차차차?',  # korean chacha
        'samba',
        u'桑巴',  # chinese samba
        u'삼바',  # kroean samba
        u'samba no p[ée]',
        'samba de gafieira',
        'samba pagode',
        u'samba ax[ée]',
        'samba\W?rock',
        'samba de roda',
        u'pachanga',
        'cuban',
        u'サンバ',
        'bachata',
        u'бачата',
        u'바차타',  # korean bachata
        u'バチャータ',
        'merengue',  # DR
        'mereng',  # haitain
        u'меренге',
        u'메렝게',  # korean merenge
        'rh?umba',
        u'倫巴',  # chinese rumba dance
        u'륨바',  # korean rumba
        'afro\W?[ck]uba\w+',
        'latin',
        'salsy',
    )
)

SALSA = Any(
    u'salsa',
    u'сальса',
    u'サルサ',
)

LADIES = Any(
    u'lad(?:y|ies)',
    u'レディース',
)
STYLING = Any(
    u'styling?',
    u'スタイリング',
)
SHINES = Any(
    u'shines?',
    u'シャイン',
)
PARTNER = Any(u'partner(?:ing)?',)
REAL_DANCE = Name(
    'LATIN_REAL_DANCE',
    Any(
        commutative_connected(
            Any(
                dance_keywords.EASY_DANCE,
                'cuban',
                'on1',
                'on2',
                'rueda',
                'cuba\w+',
                'footwork\w*',
                LADIES,
                STYLING,
                SHINES,
                PARTNER,
            ), SALSA
        ),
        commutative_connected(LADIES, Any(STYLING, SHINES, PARTNER)),
        commutative_connected(PARTNER, Any(STYLING, SHINES)),
        commutative_connected(
            Any(SALSA, AMBIGUOUS_DANCE_MUSIC),
            Any(
                LADIES,
                PARTNER,
                SHINES,
                STYLING,
            ),
        ),
        'salsa rueda',
        'rueda (?:de )?casino',
        'salser[oa]s?',
        'bachatango',
        'bachata sensual',
        'sensual\W?bachata',
        'latin\W?techni\w+',
    )
)

ALL_LATIN_STYLES = Any(REAL_DANCE, SALSA, AMBIGUOUS_DANCE_MUSIC)

FOOD = Any(
    u'소스',  # korean sause
    'spicy',
    'chili',
    'chefs?',
    'cooks?',
    'tastings?',
    'cinco de mayo',
)

DANCER = Any('queen')
GOOD_DANCE = Any(REAL_DANCE, commutative_connected(AMBIGUOUS_DANCE_MUSIC, Any(dance_keywords.EASY_DANCE, DANCER)))

#TODO(all-styles): incorporate these...."additions"
class_keywords = Any(dance_keywords.CLASS, 'batch')
all_class = Any(class_keywords, commutative_connected(dance_keywords.PERFORMANCE, class_keywords))


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE_MUSIC
    GOOD_DANCE = Any(GOOD_DANCE, SALSA)
    GOOD_BAD_PAIRINGS = [(SALSA, FOOD)]
    ADDITIONAL_EVENT_TYPE = Any('social')

    def _quick_is_dance_event(self):
        ballroom_classifier = ballroom.Style.get_classifier()(self._classified_event)
        result = ballroom_classifier.is_dance_event()
        for log in ballroom_classifier.debug_info():
            self._log(log)
        if result:
            return False
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'LATIN'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'salsa footwork',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'cha-cha',
            'samba',
            'bachata',
            'rumba',
            'merengue',
            'salsa',
            'afro-cuba',
            'afro-cuban',
            'afrocuban',
            'salsa dance',
            'ladies styling',
            'salsa on1',
            'salsa on2',
            'cuban salsa',
            'salsa cubaine',
            'salsa styling',
            'salsa shine',
            'salsa dance',
            u'サルサ',
            u'サンバ',
            u'バチャータ',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_DANCE_MUSIC, REAL_DANCE, SALSA)
