# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

TAP_DANCE = Any(
    commutative_connected(Any(
        u'step',
        u'tap',
    ), dance_keywords.EASY_DANCE),
    u'claquettes',  # french
    u'dzsiggelés',  # hungarian
    u'sapateado',  # portuguese
    u'tip\W?tap',  # italian
    u'чечетка',  # russian
)

TAP = Any(
    u'bakstelėkite',  # lithuanian
    # u'step' found too many things by itself...step by step, watch your step, one step, etc
    u'tap',
    u'tapikin',  # tagalog
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
    ADDITIONAL_EVENT_TYPE = keywords.JAM
    GOOD_BAD_PAIRINGS = [
        (Any(u'step'), Any(
            u'quick\W?step',
            u'(?:two|2)\W*step',
            u'bokwa step',
        )),
        (Any('taps?'), Any(
            u'brewer\w*',
            u'craft beer',
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
