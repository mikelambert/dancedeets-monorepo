# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp import event_types

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

DANCE_MUSIC_KEYWORDS = [
    u'莎莎',  # chinese salsa dance
    u'살사',  # korean salsa
    'salsy',
]

AMBIGUOUS_DANCE_MUSIC = Any(*DANCE_MUSIC_KEYWORDS)

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
                'cubana?',
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
    )
)

FOOD = Any(
    u'소스',  # korean sause
    'spicy',
    'chili',
    'chefs?',
    'cooks?',
    'tastings?',
    'cinco de mayo',
    'chips',  # chips n salsa
)

DANCER = Any('queen')
GOOD_DANCE = Any(
    SALSA,
    REAL_DANCE,
    commutative_connected(AMBIGUOUS_DANCE_MUSIC, Any(dance_keywords.EASY_DANCE, DANCER)),
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE_MUSIC
    GOOD_DANCE = GOOD_DANCE
    GOOD_BAD_PAIRINGS = [(SALSA, FOOD)]
    ADDITIONAL_EVENT_TYPE = Any('social')

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'SALSA'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'salsa footwork',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'cuban salsa',
            'rueda de casino',
            'salsa cubaine',
            'salsa dance',
            'salsa on1',
            'salsa on2',
            'salsa rueda',
            'salsa shine',
            'salsa styling',
            'salsa',
            u'サルサ',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
