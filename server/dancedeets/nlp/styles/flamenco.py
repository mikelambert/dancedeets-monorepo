# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

FLAMENCO_KEYWORDS = [
    u'flamenco',  # vietnamese
    u'flamenko',  # croatian
    u'flamingo',  # dutch
    u'φλαμένκο',  # greek
    u'фламенко',  # macedonian
    u'פְלָמֶנקוֹ',  # hebrew
    u'الفلامنكو',  # arabic
    u'ฟละแมนโก',  # thai
    u'フラメンコ',  # japanese
    u'弗拉門戈',  # chinese traditional
    u'弗拉门戈',  # chinese simplified
    u'플라멩코',  # korean
]
FLAMENCO = Any(*FLAMENCO_KEYWORDS)

AMBIGUOUS_DANCE = FLAMENCO


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any('festivals?',)

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'FLAMENCO'

    @classmethod
    def get_rare_search_keywords(cls):
        return FLAMENCO_KEYWORDS

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'flamenco',
            u'flamenco dance',
            u'flamenko',
            u'flamingo dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return [
            'milonga',
        ]

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_DANCE)
