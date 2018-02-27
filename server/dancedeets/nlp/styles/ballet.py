# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    u'ballet\w*',
    u'ball?ett[io]?',
    u'baletas',  # lithuanian
    u'μπαλέτο',  # greek
    u'балет\w*',  # russian
    u'בַּלֶט',  # hebrew
    u'ا?ل?باليه',  # arabic
    u'ব্যালে',  # bengali
    u'ਬੈਲੇ',  # punjabi
    u'ระบำปลายเท้า',  # thailand
    u'バレエ',  # japanese
    u'芭蕾',  # chinese
    u'발레',  # korean
    u'danza classica',
    u'danse classique',
)
AMBIGUOUS_DANCE = Any(u'bal[ée]',)

STRONG_KEYWORDS = Any(
    u'swan lake',
    u'лебединое озеро',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    SUPER_STRONG_KEYWORDS = STRONG_KEYWORDS
    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'recital',
        'gala',
        u'ガラ',
    )

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BALLET'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'baletas',
            u'balletto',
            u'μπαλέτο',
            u'בַּלֶט',
            u'芭蕾',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'balet',
            u'ballett',
            u'ballet',
            u'балет',
            u'バレエ',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(REAL_DANCE, AMBIGUOUS_DANCE)
