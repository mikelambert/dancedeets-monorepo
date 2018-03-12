# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

DANCE = Any(
    u'batonistas?',
    u'color\W?guard',
    u'maistretė',  # lithuanian
    u'majoreta',  # romanian
    u'majorete\w+',  # romanian
    u'majorettes?',  # french
    u'mazsorett',  # hungarian
    u'mažoretk\w+',  # croatian
    u'カラーガード',
    u'batol twirl\w*',
)

AMBIGUOUS_DANCE = Any(
    u'baton',
    u'twirl(?:en)?',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any('miss')

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'MAJORETTE'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'baton',
            'baton twirling',
            'batonista',
            'majorette',
            'colorguard',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return ['miss']

    @classmethod
    def _get_classifier(cls):
        return Classifier
