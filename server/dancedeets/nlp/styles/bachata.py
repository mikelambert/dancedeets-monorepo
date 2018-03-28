# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import event_types

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

BACHATA_KEYWORDS = [
    'bachata',
    u'бачата',
    u'באכטה',  # hebrew
    u'باجاتا',  # arabic
    u'바차타',  # korean bachata
    u'バチャータ',
]

BACHATA_DANCE = Any(
    'bachatango',
    'bachata sensual',
    'sensual\W?bachata',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = Any(*BACHATA_KEYWORDS)
    GOOD_DANCE = BACHATA_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BACHATA'

    @classmethod
    def get_rare_search_keywords(cls):
        return BACHATA_KEYWORDS + [
            'bachatango',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'bachata',
            u'バチャータ',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPESS

    @classmethod
    def _get_classifier(cls):
        return Classifier
