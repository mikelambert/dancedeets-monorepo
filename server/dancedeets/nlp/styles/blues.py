# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import partner_fusion
from dancedeets.nlp.street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

BLUES = Any(
    'blues',
    u'ブルース',  # japanese blues
)

AMBIGUOUS_DANCE = commutative_connected(BLUES, partner_fusion.FUSION)

GOOD_DANCE = Any(
    'slow drag',
    commutative_connected(BLUES, dance_keywords.EASY_DANCE),
)

# Event Sites:
# http://www.swingplanit.com/


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
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
        return 'BLUES'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'slow drag',
            'blues fusion',
            'blues dance',
            'blues dancing',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES + ['hop']

    @classmethod
    def _get_classifier(cls):
        return Classifier
