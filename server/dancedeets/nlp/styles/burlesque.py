# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

BURLESQUE = Any(
    'burles\w+',
    u'バーレスク',
)
CABARET = Any(
    'cabaret',
    u'キャバレー',
)
REAL_DANCE = Any(commutative_connected(BURLESQUE, CABARET))
AMBIGUOUS_DANCE = Any(BURLESQUE, CABARET)

EVENT_TYPES = Any(
    'miss',  # miss pole dance
    'show',
    'revue',
    u'recensione',  # italian
    u'revisión',  # spanish
    u'レビュー',
    'festival',
    'ball',
)
DANCE_KEYWORDS = Any(
    'burly',
    'burlies',
    'sultry',
    'moulin rouge',
    'strip\w*',
    "l'effeuillage",
    'drag',
    'strip\W?tease',
    'sexy',
    'sexi\w+',
    'tassels',
    'assels',
    'corsets?',
    'vintage',
    'sensual\w*',
    'sinnlichkeit',  # german sensuality
    'showgirl',
    'stage kitten',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = EVENT_TYPES
    DANCE_KEYWORDS = DANCE_KEYWORDS

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        result = self.burlesque_cabaret_title()
        if result:
            return result

        return False

    @base_auto_classifier.log_to_bucket('burlesque_cabaret_title')
    def burlesque_cabaret_title(self):
        is_dance_ish = self.is_dance_ish()
        if is_dance_ish and (self._title_has(BURLESQUE) or self._title_has(CABARET)):
            return 'burlesque/cabaret title and a dance-event'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BURLESQUE'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'burlesque',
            'burlesco',
            'burleske',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return ['revue']

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_DANCE)
