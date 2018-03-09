# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

TRADITIONAL_DANCE_LIST = [
    u'dance traditionnelle',  # french
    u'dans tradițional',  # romanian
    u'danza tradicional',  # spanish
    u'danza tradizionale',  # italian
    u'dança tradicional',  # portuguese
    u'geleneksel dans',  # turkish
    u'hagyományos tánc',  # hungarian
    u'perinteinen tanssi',  # finnish
    u'tarian tradisional',  # malay
    u'tradicinis šokis',  # lithuanian
    u'tradicionalni ples',  # croatian
    u'tradisjonell dans',  # norwegian
    u'tradisyonal na sayaw',  # tagalog
    u'traditional dance',  # english
    u'traditionel dans',  # danish
    u'traditionele dans',  # dutch
    u'traditionell dans',  # swedish
    u'traditioneller tanz',  # german
    u'tradiční tanec',  # czech
    u'tradycyjny taniec',  # polish
    u'điệu nhảy truyền thống',  # vietnamese
    u'παραδοσιακός χορός',  # greek
    u'традиционален танц',  # macedonian
    u'традиционный танец',  # russian
    u'ריקוד מסורתי',  # hebrew
    u'الرقص التقليدي',  # arabic
    u'เต้นรำแบบดั้งเดิม',  # thai
    u'伝統舞踊',  # japanese
    u'传统舞蹈',  # chinese simplified
    u'傳統舞蹈',  # chinese traditional
    u'전통 무용',  # korean
]

FOLK_DANCE_LIST = [
    u'baile folclórico',  # spanish
    u'dans popular',  # romanian
    u'danse folklorique',  # french
    u'danza popolare',  # italian
    u'dança folclórica',  # portuguese
    u'folk dance',  # english
    u'folkdans',  # swedish
    u'folkedans',  # norwegian
    u'halk dansı',  # turkish
    u'kansantanssi',  # finnish
    u'katutubong sayaw',  # tagalog
    u'liaudies šokiai',  # lithuanian
    u'lidový tanec',  # czech
    u'múa dân gian',  # vietnamese
    u'narodni ples',  # croatian
    u'népi tánc',  # hungarian
    u'taniec ludowy',  # polish
    u'tarian rakyat',  # malay
    u'volksdans',  # dutch
    u'volkstanz',  # german
    u'λαϊκοί χοροί',  # greek
    u'народен танц',  # macedonian
    u'народный танец',  # russian
    u'ריקוד עם',  # hebrew
    u'الرقص الشعبي',  # arabic
    u'การเต้นรำพื้นบ้าน',  # thai
    u'フォークダンス',  # japanese
    u'民間舞蹈',  # chinese traditional
    u'民间舞蹈',  # chinese simplified
    u'포크 댄스',  # korean
]

TRADITIONAL = Any(
    u'geleneksel',  # turkish
    u'hagyományos',  # hungarian
    u'perinteinen',  # finnish
    u'tradi[ctțz][ij]onn?[ae]l\w*',
    u'tradisyonal na',  # tagalog
    u'tradiční',  # czech
    u'tradicinis',  # lithuanian
    u'tradycyjny',  # polish
    u'truyền thống',  # vietnamese
    u'παραδοσιακός',  # greek
    u'традиционален',  # macedonian
    u'традиционный',  # russian
    u'מסורתי',  # hebrew
    u'التقليدي',  # arabic
    u'แบบดั้งเดิม',  # thai
    u'伝統',  # japanese
    u'传统',  # chinese simplified
    u'傳統',  # chinese traditional
    u'전통',  # korean
)

FOLK = Any(
    u'dân gian',  # vietnamese
    u'folclóric\w+',  # spanish
    u'folclórica',  # portuguese
    u'folklorique',  # french
    u'folk',
    u'folke',  # danish
    u'halk',  # turkish
    u'kansan',  # finnish
    u'katutubong',  # tagalog
    u'liaudies',  # lithuanian
    u'lidový',  # czech
    u'ludowy',  # polish
    u'narodni',  # croatian
    u'népi',  # hungarian
    u'popolare',  # italian
    u'rakyat',  # malay
    u'volks',  # dutch
    u'volks',  # german
    u'λαϊκοί',  # greek
    u'народе?н\w+',  # russian
    u'ריקוד עם',  # hebrew
    u'الشعبي',  # arabic
    u'พื้นบ้าน',  # thai
    u'フォーク',  # japanese
    u'民間',  # chinese traditional
    u'民间',  # chinese simplified
    u'포크',  # korean
)

GOOD_DANCE = Any(
    commutative_connected(Any(FOLK, TRADITIONAL), dance_keywords.EASY_DANCE),
    # mazurka
    u'mazurka',
    u'mazurek',
    u'мазурка',
    # krakowiak
    u'krakowiak',
    u'krakauer',
    u'краковяк'
    u'cracovienne',
    # balfolk
    u'balfolk',  # english
    u'balfour',  # french
    u'balvolk',  # german
    u'バフォフォーク',  # japanese
    #
    u'liscio',
)

# Not yet used
BALFOLK_DANCE_TYPES = Any(
    u'schottisches?',
    u'bourrées?'
    u'waltz',
    u'polkas',
    u'mazurkas'
    u'polska',
    u'chapelloise',
    u'gigues?',
    u'circassian circle',
    u'breton dance',
    u'contra dances',
)

AMBIGUOUS_DANCE = Any(
    u'bal folk',
    u'folk bal',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'FOLK'

    @classmethod
    def get_rare_search_keywords(cls):
        return FOLK_DANCE_LIST + TRADITIONAL_DANCE_LIST

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'bal folk',
            u'balfolk',
            u'folk dance',
            u'traditional dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(GOOD_DANCE)
