# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import partner

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any('chicago(?: style)? stepp(?:ing?|ers?)')


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    SUPER_STRONG_KEYWORDS = REAL_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'CHICAGO_STEPPING'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'chicago steppin',
            'chicago stepping',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return []

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES + ['event']

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(REAL_DANCE)
