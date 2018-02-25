# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import partner

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    'lindy\W?hop\w*',
    u'リンディ',  # japanese lindy
    u'린디',  # korean lindy
    'east coast swing',
    'solo jazz',
    'solo charleston',
    'partner charleston',
    'carolina shag',
    'collegiate shag',
    'st\W? louis shag',
    'slow drag',
    'balboa\w*',
    'authentic jazz',
)

AMBIGUOUS_WORDS = Any(
    'swing\w*',
    u'سوينغ',  # arabic swing
    'charleston',
    'shag',
    'ecs',
)

AMBIGUOUS_DANCE_MUSIC = Any(
    'blues',
    u'ブルース',  # japanese blues
)

# Event Sites:
# http://www.swingplanit.com/


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = Any(AMBIGUOUS_WORDS, AMBIGUOUS_DANCE_MUSIC)
    GOOD_DANCE = REAL_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'festival',
        'marathon',
    )

    def _quick_is_dance_event(self):
        result = ballroom.Style.get_classifier()(self._classified_event).is_dance_event()
        if result:
            return False
        return True

    def is_dance_event(self):
        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        return False


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
            'east coast swing',
            'ecs',
            'west coast swing',
            'swing out',
            'lindy hop',
            'lindy',
            'balboa',
            'solo jazz',
            'solo charleston',
            'partner charleston',
            'carolina shag',
            'collegiate shag',
            'st louis shag',
            'modern jive',
            'jitterbug',
            'slow drag',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES + ['hop']

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_WORDS, REAL_DANCE)
