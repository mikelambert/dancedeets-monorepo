# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

ZAP = Any(
    u'zapateado',  # thai
    u'zapateadonun',  # turkish
    u'сапатеадо',  # russian
    u'זאפטאדו',  # hebrew
    u'サパテアド',  # japanese
    u'자파 ?타도',  # korean
)
AMBIGUOUS_DANCE = ZAP


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'ZAPATEADO'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'zapateado',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
