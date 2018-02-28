# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

GOOD_DANCE = Any(
    u'bhangra',
    u'भांगड़ा',  # hindi
    u'ਭੰਗੜਾ',  # punjabi
    u'бхангра',  # russian
    u'בהאנגרה',  # hebrew
    u'بنجابية',  # arabic
    u'รงค์',  # thai
    u'バングラ',  # japanese
    u'般格拉',  # chinese simplified
    u'반 ?그라',  # korean
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BHANGRA'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'भांगड़ा',  # hindi
            u'ਭੰਗੜਾ',  # punjabi
            u'бхангра',  # russian
            u'בהאנגרה',  # hebrew
            u'بنجابية',  # arabic
            u'รงค์',  # thai
            u'バングラ',  # japanese
            u'般格拉',  # chinese simplified
            u'반 ?그라',  # korean
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'bhangra',
            u'bhangra dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(GOOD_DANCE)
