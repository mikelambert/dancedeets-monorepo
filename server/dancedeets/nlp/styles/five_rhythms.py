# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

FIVE_RHYTHMS = [
    u'5 irama',  # malay
    u'5 nhịp điệu',  # vietnamese
    u'5 rhythmen',  # german
    u'5 rhythms',  # english, tagalog
    u'5 ritimler',  # turkish
    u'5 ritmai',  # lithuanian
    u'5 ritmes',  # dutch
    u'5 ritmi',  # italian
    u'5 ritmos',  # portuguese, spanish
    u'5 ritmova',  # croatian
    u'5 ritmuri',  # romanian
    u'5 ritmus',  # hungarian
    u'5 rythmes',  # french
    u'5 rytmer',  # danish, norwegian, swedish
    u'5 rytmiä',  # finnish
    u'5 rytmów',  # polish
    u'5 rytmů',  # czech
    u'5 ρυθμούς',  # greek
    u'5 ритми',  # macedonian
    u'5 ритмов',  # russian
    u'5 מקצבים',  # hebrew
    u'5 إيقاعات',  # arabic
    u'5 จังหวะ',  # thai
    u'5 리듬',  # korean
    u'5リズム',  # japanese
    u'5節奏',  # chinese traditional
    u'5节奏',  # chinese simplified
]
REAL_DANCE = Any(*FIVE_RHYTHMS)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    SUPER_STRONG_KEYWORDS = REAL_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'FIVE_RHYTHMS'

    @classmethod
    def get_rare_search_keywords(cls):
        return FIVE_RHYTHMS

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            '5 rhythms',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
