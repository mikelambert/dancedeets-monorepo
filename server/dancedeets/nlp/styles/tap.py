# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

TAP_DANCE = Any(
    u'claquettes',  # french
    u'dzsiggelés',  # hungarian
    u'sapateado',  # portuguese
    u'tip\W?tap',  # italian
    u'чечетка',  # russian
)

TAP = Any(
    u'bakstelėkite',  # lithuanian
    u'tap',
    u'tapp\w+',
    u'step',
    u'stepp\w*',  # polish
    u'tapikin ang',  # tagalog
    u'допрете',  # macedonian
    u'סטפס',  # hebrew
    u'الصنبور',  # arabic
    u'แตะ',  # thai
    u'タップ',  # japanese
    u'踢踏',  # chinese simplified
    u'탭',  # korean
)

KEYWORDS = Any(
    'hoofers?',
    'shim\W?sham',
)

REAL_DANCE = Any(
    TAP_DANCE,
    'rhythm\W?tap',
    'theater\W?tap',
    'broadway\W?tap',
    'body\W?percussion',
)

AMBIGUOUS_DANCE = TAP


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    REAL_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    DANCE_KEYWORDS = KEYWORDS
    GOOD_BAD_PAIRINGS = [
        (Any('step'), Any(
            'quick\W?step',
            '(?:two|2)\W*step',
        )),
    ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'TAP'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'tap',
            u'tap dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_DANCE)
