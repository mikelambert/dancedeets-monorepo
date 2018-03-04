# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import ballroom_keywords
from dancedeets.nlp.styles import partner

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

GOOD_DANCE = Any(*ballroom_keywords.WALTZ)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE

    def _quick_is_dance_event(self):
        result = ballroom.Style.get_classifier()(self._classified_event).is_dance_event()
        if result:
            return False
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'WALTZ'

    @classmethod
    def get_rare_search_keywords(cls):
        return ballroom_keywords.WALTZ

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'waltz',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(GOOD_DANCE)
