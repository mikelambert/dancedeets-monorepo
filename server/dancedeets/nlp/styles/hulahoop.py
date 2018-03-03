# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

KEYWORDS = [
    u'hula\W?hoop',
    u'hoelahoep',
    u'хула хоп',  # macedonian
    u'הולה הופה',  # hebrew
    u'الهولا طارة',  # arabic
    u'ฮูลาห่วง',  # thai
    u'フラフープ',  # japanese
    u'呼啦圈',  # chinese simplified
    u'훌라후프',  # korean
]
AMBIGUOUS_DANCE = Any(*KEYWORDS)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'HULAHOOP'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'hula hoop',
            u'hula hoop dance',
            u'フラフープ',
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
