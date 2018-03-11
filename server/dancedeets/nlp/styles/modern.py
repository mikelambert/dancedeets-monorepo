# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import contemporary

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

TECHNIQUES = Any(
    'horton',
    'graham',
)

MODERN = Any(
    u'modern\w*',
    u'moden',
    u'hiện đại',
    u'nowoczesny',
    u'μοντέρνος',
    u'модерен',
    u'модерн',
    u'מודרני',
    u'الحديث',
    u'การเต้นรำสมัยใหม่',
    u'モダン',
)

REAL_DANCE = Any(
    commutative_connected(MODERN, contemporary.CONTEMPORARY),
    connected(TECHNIQUES, Any('techniques?')),
)

AMBIGUOUS_DANCE = MODERN


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(u'recital',)
    GOOD_BAD_PAIRINGS = [
        (MODERN, Any('modern jive')),
    ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'MODERN'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'modern dans',
            u'modern tánc',
            u'moderne dans',
            u'moderner tanz',
            u'nhảy hiện đại',
            u'モダンダンス',
            u'современный танец',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'modern dance',
            u'danse moderne',
            u'danza moderna',
            u'modern',
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
