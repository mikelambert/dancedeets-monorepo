# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.street import keywords
from dancedeets.nlp.styles import partner
from dancedeets.nlp.ballroom import classifier as ballroom_classifier

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

ARGENTINE = Any(
    'argentin\w*',
    u'アルゼンチン',
    u'阿根廷',
    u'아르헨티나',
    u'аргентинское',  # russian
)

TANGO = Any(
    'tango',
    u'タンゴ',
    u'探戈',
    u'탱고',
    u'танго',  # russian
)
MILONGA = Any(
    'milongas?',
    u'ミロンガ',
    u'밀롱가',
)
TANGO_TYPES = Any(
    MILONGA,
    'traditional',
    'nuevo',
    u'ヌオーバ',
    u'새로운',
    'vals',
    u'バルス',
    u'왈츠',
    'alternative',
)
REAL_DANCE = commutative_connected(ARGENTINE, TANGO)

AMBIGUOUS_WORDS = Any(
    MILONGA,
    # 'traditional dance' or 'alternative dance' would trigger...
    #TANGO_TYPES,
    TANGO,
    commutative_connected(TANGO_TYPES, TANGO),
)

EXTRAS = Any(ARGENTINE, TANGO_TYPES, keywords.EASY_DANCE)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_WORDS
    GOOD_DANCE = REAL_DANCE
    ADDITIONAL_EVENT_TYPE = Any('meeting', 'incontro', 'festival', 'marathon', 'milongas?')
    GOOD_BAD_PAIRINGS = [
        (TANGO, Any('whiskey tango')),
    ]

    def _quick_is_dance_event(self):
        ballroom = ballroom_classifier.is_many_ballroom_styles(self._classified_event)
        if ballroom[0]:
            return False
        return True

    def is_dance_event(self):
        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        result = self.is_tango()
        if result:
            return result

        return False

    def is_tango(self):
        if (self._title_has(TANGO) or self._title_has(MILONGA)) and len(list(self._get(EXTRAS))) >= 2:
            return 'has tango title and tango/dance keywords'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'TANGO'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'argentine tango',
            'tango',
            'milonga',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_WORDS, REAL_DANCE)
