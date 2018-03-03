# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

KIZOMBA = Any(
    'kizomba\w*',
    u'キゾンバ',
    'semba',
    'tarraxa',
    'tarraxinha',
    u'semba',  # thai
    u'самбийского',  # russian
    u'семба',  # macedonian
    u'סמבה',  # hebrew
    u'セムバ',  # japanese
    u'桥西',  # chinese simplified
    u'橋西',  # chinese traditional
    u'세미 바',  # korean
)
AMBIGUOUS_DANCE = KIZOMBA


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any('congress',)

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'KIZOMBA'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'kizomba',
            'kizomba dance',
            u'キゾンバ',
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
