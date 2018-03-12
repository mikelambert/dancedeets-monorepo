# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

BURLESQUE = Any(
    u'burles[ckqz]\w*',
    u'бурлеск\w*',  # russian
    u'בּוּרלֶסקָה',  # hebrew
    u'バーレスク',  # japanese
    u'滑稽戏',  # chinese simplified
    u'滑稽戲',  # chinese traditional
)

CABARET = Any(
    u'cabaret\w*',  # dutch, english, french, italian, romanian, spanish, tagalog
    u'cabaré\w*',  # portuguese
    u'kabaree\w*',  # finnish
    u'kabaret\w*',  # czech, danish, malay, norwegian, polish
    u'kabarett\w*',  # german
    u'kabaretas\w*',  # lithuanian
    u'kabaré\w*',  # hungarian
    u'quán rượu',  # vietnamese
    u'καμπαρέ',  # greek
    u'кабаре',  # macedonian
    u'קַבָּרֶט',  # hebrew
    u'ملهى',  # arabic
    u'คาบาเร่ต์',  # thai
    u'キャバレー',  # japanese
    u'歌舞表演',  # chinese simplified
    u'카바레',  # korean
)
REAL_DANCE = Any(commutative_connected(BURLESQUE, CABARET))
# Intentionally do not include cabaret in AMBIGUOUS_DANCE
# There are too many 1920s non-burlesque cabaret shows, in all languages.
AMBIGUOUS_DANCE = Any(BURLESQUE)

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

    def perform_extra_checks(self):
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
