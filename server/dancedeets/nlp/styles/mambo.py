# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import ballroom_keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

MAMBO = Any(*ballroom_keywords.MAMBO)
GOOD_DANCE = MAMBO


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
    GOOD_BAD_PAIRINGS = [
        (
            MAMBO,
            Any(
                u'edm',
                u'house music',
                u'ibiza',
                u'ex forno mambo',
                u'mambo club',
                u'mambo brothers',  # don't dj mambo music at all...
                u'mambo beach club',
                u'café mambo',
                u'cafe mambo',
                u'mambo italiano',
            )
        ),
    ]

    def _quick_is_dance_event(self):
        ballroom_classifier = ballroom.Style.get_classifier()(self._classified_event, debug=self._debug)
        result = ballroom_classifier.is_dance_event()
        for log in ballroom_classifier.debug_info():
            self._log(log)
        if result:
            return False
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'MAMBO'

    @classmethod
    def get_rare_search_keywords(cls):
        return ballroom_keywords.MAMBO

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'mambo',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
