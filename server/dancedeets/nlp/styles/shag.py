# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import event_types
from dancedeets.nlp.street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

SHAG = Any(
    'carolina shag',
    'collegiate shag',
    'st\W? louis shag',
)

AMBIGUOUS_DANCE = Any('shag',)

# Event Sites:
# http://www.swingplanit.com/


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    GOOD_DANCE = SHAG
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
        return 'SHAG'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'carolina shag',
            'collegiate shag',
            'st louis shag',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPESS + ['hop']

    @classmethod
    def _get_classifier(cls):
        return Classifier
