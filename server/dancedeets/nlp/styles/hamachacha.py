# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom_keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

GOOD_DANCE = connected(
    Any(
        u'フリー',
        u'ハマ',
        u'hama',
        u'free',
    ),
    Any(*ballroom_keywords.CHACHA),
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'HAMACHACHA'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'フリーチャチャ',
            u'ハマチャチャ',
        ]

    @classmethod
    def _get_classifier(cls):
        return Classifier
