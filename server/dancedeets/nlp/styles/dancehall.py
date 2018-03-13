# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    'ragga\W?jamm?',
    u'댄스 ?레게',  # korean reggae dance
    u'레게 ?댄스',  # korean reggae dance
    u'דאנסהול',  # hebrew dancehall
)

DANCEHALL = Any(
    u'dancehall',
    u'ダンスホール',
    u'댄스홀',
)

REGGAE = Any(
    u'rege muzika',  # croatian
    u'reggae',  # english
    u'ρέγκε',  # greek
    u'регги',  # russian
    u'реге',  # macedonian (not english letters)
    u'רגאיי',  # hebrew
    u'الريغي',  # arabic
    u'เร้กเก้',  # thai
    u'レゲエ',  # japanese
    u'雷鬼',  # chinese simplified
    u'레게',  # korean
)

REGGAETON = Any(
    u"רג 'טון",  # hebrew
    u'reggaeton\w*',  # english
    u'reguetón',  # spanish
    u'реггитон',  # russian
    u'регетон',  # macedonian
    u'レゲトン',  # japanese
    u'레게 ?톤',  # korean
)

SOCA = Any(u'soca',)

CALYPSO = Any(
    u'calipso',  # romanian
    u'calypso',  # english
    u'kalipso',  # croatian
    u'türkü',  # turkish
    u'είδος χορού των δυτικών ινδίων',  # greek
    u'калипсо',  # macedonian
    u'קליפסו',  # hebrew
    u'كاليبسو',  # arabic
    u'คาลิปโซ่',  # thai
    u'カリプソ',  # japanese
    u'卡吕普索',  # chinese simplified
    u'卡呂普索',  # chinese traditional
    u'칼립소',  # korean
)

AMBIGUOUS_DANCE = Any(
    DANCEHALL,
    REGGAE,
    REGGAETON,
    SOCA,
    CALYPSO,
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    REAL_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    INCLUDE_PARTY_EVENTS = False

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'DANCEHALL'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'ダンスホール',
            u'レゲエ',  # japanese
            u'レゲトン',  # japanese
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'dancehall',
            'ragga jam',
            'reggae',
            'reggaeton',
            'soca',
            'calypso',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
