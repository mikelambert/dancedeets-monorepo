# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

LINE_DANCE = Any(
    # with dance suffix
    '(?:baltimore|b\W?more|chicago|chi\W?town)\Wline\W?danc\w*',
    '(?:urban|hip\W?hop|r\W+b)\W?line\W?danc\w*',
    # without dance suffix
    'soul\W?line\w*',
    'chitown slide',
    'cleveland shuffle',
    'wobble line\w*',
    'zydeco line\w*',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = LINE_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'convention',
        'marathon',
        'brunch',
        'throwdown',
        'party',
    )

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'SOULLINE'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'soul line',
            'baltimore line',
            'urban line',
            'wobble line',
            'zydeco',
            'chicago line',
            'hip-hop line',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
