# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

KEYWORDS = [
    u'zumba\w*',  # thai
    u'зумба',  # russian
    u'זומבה',  # hebrew
    u'زومبا',  # arabic
    u'ズンバ',  # japanese
    u'尊巴舞',  # chinese simplified
    u'줌바',  # korean
]
ZUMBA = Any(*KEYWORDS)

GOOD_DANCE = ZUMBA


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'ZUMBA'

    @classmethod
    def get_rare_search_keywords(cls):
        return KEYWORDS

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'zumba',
            u'zumba dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
