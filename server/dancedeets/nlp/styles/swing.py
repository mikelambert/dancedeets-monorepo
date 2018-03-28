# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import authentic_jazz
from dancedeets.nlp.styles import balboa
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import charleston
from dancedeets.nlp.styles import east_coast_swing
from dancedeets.nlp.styles import jitterbug
from dancedeets.nlp.styles import lindy
from dancedeets.nlp.street import keywords
from dancedeets.nlp.styles import shag

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    authentic_jazz.AUTHENTIC_JAZZ,
    balboa.BALBOA,
    charleston.CHARLESTON,
    east_coast_swing.GOOD_DANCE,
    jitterbug.JITTERBUG,
    lindy.LINDY,
    shag.SHAG,
)

AMBIGUOUS_WORDS = Any(
    'swing\w*',
    u'سوينغ',  # arabic swing
    charleston.AMBIGUOUS_DANCE,
    east_coast_swing.AMBIGUOUS_DANCE,
    shag.AMBIGUOUS_DANCE,
)

# Event Sites:
# http://www.swingplanit.com/


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_WORDS
    GOOD_DANCE = REAL_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        u'festival',
        u'marathon',
        keywords.JAM,
    )

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
        return 'SWING'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'swing dance',
            'swing out',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES + ['hop']

    @classmethod
    def _get_classifier(cls):
        return Classifier
