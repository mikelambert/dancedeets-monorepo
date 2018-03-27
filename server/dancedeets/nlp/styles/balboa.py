# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import partner
from dancedeets.nlp.street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

BALBOA = Any('balboa\w*', u'бальбоа')

# Event Sites:
# http://www.swingplanit.com/


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = BALBOA
    ADDITIONAL_EVENT_TYPE = Any(
        u'festival',
        u'marathon',
        keywords.JAM,
    )

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BALBOA'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'balboa',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES + ['hop']

    @classmethod
    def _get_classifier(cls):
        return Classifier
