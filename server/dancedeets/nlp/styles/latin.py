# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import bachata
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import ballroom_keywords
from dancedeets.nlp.styles import merengue
from dancedeets.nlp.styles import partner
from dancedeets.nlp.styles import salsa

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

DANCE_MUSIC_KEYWORDS = [
    u'莎莎',  # chinese salsa dance
    u'살사',  # korean salsa
    u'pachanga',
    'cuban',
    'latin\W?american',
    'latin',
    'salsy',
]
DANCE_MUSIC_KEYWORDS.extend(ballroom_keywords.CHACHA)
DANCE_MUSIC_KEYWORDS.extend(ballroom_keywords.RUMBA)
DANCE_MUSIC_KEYWORDS.extend(merengue.MERENGUE_KEYWORDS)
DANCE_MUSIC_KEYWORDS.extend(salsa.DANCE_MUSIC_KEYWORDS)

AMBIGUOUS_DANCE_MUSIC = Name('LATIN_AMBIGUOUS_DANCE_MUSIC', Any(*DANCE_MUSIC_KEYWORDS))

REAL_DANCE = Name(
    'LATIN_REAL_DANCE',
    Any(
        commutative_connected(salsa.LADIES, Any(salsa.STYLING, salsa.SHINES, salsa.PARTNER)),
        commutative_connected(salsa.PARTNER, Any(salsa.STYLING, salsa.SHINES)),
        commutative_connected(
            Any(AMBIGUOUS_DANCE_MUSIC),
            Any(
                salsa.LADIES,
                salsa.PARTNER,
                salsa.SHINES,
                salsa.STYLING,
            ),
        ),
        salsa.GOOD_DANCE,
        bachata.BACHATA_DANCE,
        'latin\W?techni\w+',
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
    salsa.SALSA,
    REAL_DANCE,
    commutative_connected(AMBIGUOUS_DANCE_MUSIC, Any(dance_keywords.EASY_DANCE, DANCER)),
)

#TODO(all-styles): incorporate these...."additions"
class_keywords = Any(dance_keywords.CLASS, 'batch')
all_class = Any(class_keywords, commutative_connected(dance_keywords.PERFORMANCE, class_keywords))


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE_MUSIC
    GOOD_DANCE = GOOD_DANCE
    GOOD_BAD_PAIRINGS = [(salsa.SALSA, FOOD)]
    ADDITIONAL_EVENT_TYPE = Any('social')

    def _quick_is_dance_event(self):
        ballroom_classifier = ballroom.Style.get_classifier()(self._classified_event, debug=self._debug)
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
            'ladies styling',
            'ladies shine',
            'partner styling',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'ladies styling',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
