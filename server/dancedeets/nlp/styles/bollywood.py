# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

AMBIGUOUS_DANCE = Any(
    u'bollywood',
    u'बॉलीवुड',  # hindi
    u'ਬਾਲੀਵੁੱਡ',  # punjabi
    u'ljubav',  # croatian
    u'боливуд',  # macedonian
    u'болливуд',  # russian
    u'בוליווד',  # hebrew
    u'بوليوود',  # arabic
    u'บอลลีวูด',  # thai
    u'ボリウッド',  # japanese
    u'宝莱坞',  # chinese simplified
    u'寶萊塢',  # chinese traditional
    u'볼리우드',  # korean
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BOLLYWOOD'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'bollywood',
            u'बॉलीवुड',  # hindi
            u'ਬਾਲੀਵੁੱਡ',  # punjabi
            u'ljubav',  # croatian
            u'боливуд',  # macedonian
            u'болливуд',  # russian
            u'בוליווד',  # hebrew
            u'بوليوود',  # arabic
            u'บอลลีวูด',  # thai
            u'ボリウッド',  # japanese
            u'宝莱坞',  # chinese simplified
            u'寶萊塢',  # chinese traditional
            u'볼리우드',  # korean
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'bollywood',
            u'bollywood dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
