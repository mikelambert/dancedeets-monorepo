# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import ballroom_keywords
from dancedeets.nlp.styles import partner

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

GOOD_DANCE = Any(*ballroom_keywords.CHACHA)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
    GOOD_BAD_PAIRINGS = [
        (Any(u'チャチャ'), Any(u'フリー', u'ハマ')),
        (Any(u'chachapoyas'), Any(u'chachapoyas')),  # a peruvian city
    ]

    def _quick_is_dance_event(self):
        ballroom_classifier = ballroom.Style.get_classifier()(self._classified_event)
        result = ballroom_classifier.is_dance_event()
        for log in ballroom_classifier.debug_info():
            self._log(log)
        if result:
            return False
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'CHACHA'

    @classmethod
    def get_rare_search_keywords(cls):
        return ballroom_keywords.CHACHA

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'cha cha',
            'cha cha cha',
            'chacha',
            'chachacha',
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
