# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

GOOD_DANCE = Any(
    u'c[aá]n\W?c[aá]n',
    u'k[aá]n\W?k[aá]n',
    u'κανκάν',  # greek
    u'канкан',  # macedonian
    u'יכוליכול',  # hebrew
    u'캔칸',  # korean
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
    GOOD_BAD_PAIRINGS = [
        (
            Any('french can\W?can'),
            Any(
                'cine\w*',
                '102',  # minutes
                'subtitles?',
            )
        ),
    ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'CANCAN'

    @classmethod
    def get_rare_search_keywords(cls):
        return

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'cancan',
            'can-can',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
