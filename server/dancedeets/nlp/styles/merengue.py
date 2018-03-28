# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

MERENGUE_KEYWORDS = [
    'merengue',  # DR
    'mereng',  # haitian
    u'меренге',  # macedonian, russian
    u'מרנגה',  # hebrew
    u'ميرينجو',  # arabic
    u'メレンゲ',  # japanese
    u'梅伦格',  # chinese simplified
    u'梅倫格',  # chinese traditional
    u'메렝게',  # korean
]


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = Any(*MERENGUE_KEYWORDS)

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'MERENGUE'

    @classmethod
    def get_rare_search_keywords(cls):
        return MERENGUE_KEYWORDS

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'merengue',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
