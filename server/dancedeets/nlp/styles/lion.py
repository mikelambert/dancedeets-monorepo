# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

LION = Any(
    'lion',
    u'löwen',  # german
    u'león',  # spanish
    u'leone',  # italian
    u'lví',  # czech
    u'lwa',  # polish
    u'ライオン',
    u'사자',
    u'獅',
    u'狮',
)

DRAGON = Any(
    'dragon',
    u'ドラゴン',
    u'용의',
    u'龍',
    u'龙',
)
AMBIGUOUS_DANCE = Any(LION)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'parade',
        'chinese new year',
        'cny',
    )
    GOOD_BAD_PAIRINGS = [
        (Any('lion'), Any(
            'lion\W?king',
            'disney',
        )),
    ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'LION'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'ライオンダンス',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'lion dance',
            u'舞獅',
            u'龍舞',
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
