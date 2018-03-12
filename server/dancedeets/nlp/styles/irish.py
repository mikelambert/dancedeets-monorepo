# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import tap

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

AMBIGUOUS_DANCE = Any(
    'jigs',
    u'джига',
)

IRISH = Any(
    u'irl[aä]nd\w*',
    u'ierse',  # dutch
    u'irisc?h\w*',
    u'irlantilaista',  # finnish
    u'irsk',  # norwegian
    u'irski',  # croatian
    u'irský',  # czech
    u'islamas',  # lithuanian
    u'ír',  # hungarian
    u'ιρλανδικό',  # greek
    u'ирландски\w*',  # russian
    u'ирски',  # macedonian
    u'ריקוד אירי',  # hebrew
    u'الأيرلندية',  # arabic
    u'การเต้นรำของชาวไอริช',  # thai
    u'アイルランドの',  # japanese
    u'愛爾蘭',  # chinese traditional
    u'爱尔兰',  # chinese simplified
    u'아일랜드',  # korean
)

STEP = Any('step',)

GOOD_DANCE = Any(
    commutative_connected(Any(IRISH, 'reel'), dance_keywords.EASY_DANCE),
    commutative_connected(IRISH, tap.TAP),
    commutative_connected(IRISH, Any(
        STEP,
        u'hard shoe',
        u'soft show',
        u'set',
        u'c[eé]il[ií](?:dh)?',
    )),
    u'riverdance',
    u'sean-nós',
    # jigs!
    'light jigs?',
    'slip jigs?',
    'single jigs?',
    'double jigs?',
    'hop jigs?',
    'treble jigs?',
    'straight jigs?',
    'sand jigs?',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
    ADDITIONAL_EVENT_TYPE = Any('bal')

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'IRISH'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'jigs dance',
            u'reel dance',
            u'irish set',
            u'irish step',
            u'irish hard shoe',
            u'irish soft shoe',
            u'riverdance',
            u'sean-nós',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [u'irish', u'irish dance', u'irish jig']

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
