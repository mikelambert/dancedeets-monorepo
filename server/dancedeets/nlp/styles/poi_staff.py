# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

POI = Any(
    u'poi',  # english
    u'ポイ',  # japanese
    u'포이',  # korean
)

FIRE = Any(
    u'apoy',  # tagalog
    u'ateş',  # turkish
    #u'brand', # danish
    u'brann',  # norwegian
    u'foc',  # romanian
    u'feu',  # french
    u'fuego',  # spanish
    u'fuoco',  # italian
    u'fogo',  # portuguese
    u'eld',  # swedish
    u'feuer',  # german
    u'fire dance',  # english
    u'palo',  # finnish
    u'požáru',  # czech
    u'ognia',  # polish
    #u'tarian api', # malay
    u'tűz',  # hungarian
    u'ugnies',  # lithuanian
    u'vatreni',  # croatian
    u'vuur',  # dutch
    u'bốc lửa',  # vietnamese
    u'φωτιά',  # greek
    u'оган',  # macedonian
    u'огненный',  # russian
    u'אש',  # hebrew
    u'النار',  # arabic
    u'ไฟ',  # thai
    u'火災',  # japanese
    u'火',  # chinese simplified
    u'불',  # korean
)

STAFF = Any(
    'staff',
    u'スタッフ',
)

GOOD_DANCE = Any(
    POI,
    commutative_connected(Any(FIRE, STAFF), dance_keywords.EASY_DANCE),
    'contact staff',
)

FIRE_KEYWORDS = [
    u'apoy sayaw',  # tagalog
    u'ateş dansı',  # turkish
    u'branddans',  # danish
    u'branndans',  # norwegian
    u'dans de foc',  # romanian
    u'danse du feu',  # french
    u'danza del fuego',  # spanish
    u'danza del fuoco',  # italian
    u'dança de fogo',  # portuguese
    u'elddans',  # swedish
    u'feuertanz',  # german
    u'fire dance',  # english
    u'palo tanssia',  # finnish
    u'tanec požáru',  # czech
    u'taniec ognia',  # polish
    u'tarian api',  # malay
    u'tűz tánc',  # hungarian
    u'ugnies šokis',  # lithuanian
    u'vatreni ples',  # croatian
    u'vuur dans',  # dutch
    u'điệu nhảy bốc lửa',  # vietnamese
    u'χορός φωτιά',  # greek
    u'оган танц',  # macedonian
    u'огненный танец',  # russian
    u'ריקוד אש',  # hebrew
    u'رقصة النار',  # arabic
    u'เต้นรำไฟ',  # thai
    u'火災のダンス',  # japanese
    u'火舞',  # chinese simplified
    u'불춤',  # korean
]

POI_KEYWORDS = [
    u'poi',  # english
    u'полизоя',  # russian
    u'פוי',  # hebrew
    u'البوي',  # arabic
    u'ポイ',  # japanese
    u'포이',  # korean
]


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
    ADDITIONAL_EVENT_TYPE = Any()

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'POI_STAFF'

    @classmethod
    def get_rare_search_keywords(cls):
        return FIRE_KEYWORDS + POI_KEYWORDS

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'poi',
            u'poi dance',
            u'fire dance',
            u'contact staff',
            u'staff dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(GOOD_DANCE,)
