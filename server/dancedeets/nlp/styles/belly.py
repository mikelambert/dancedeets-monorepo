# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

NON_BELLY_AMBIGUOUS_DANCE = Any(
    u'شرقي‎',  # arabic, but means 'oriental'
    u'بلدي‎',  # arabic, but means 'folk'
    # for an explanation of these, see http://www.shira.net/musings/dance-by-any-other-name.htm
    'oriental',  # oriental dance
    'egyptian',  # egyptian dance
    'middle eastern',  # middle eastern dance
    'arabe',
    'araba',
    'arabic',
    u'itämais\w+',  # oriental finnish
    'ats',
)

BELLY = Any(
    u'bauch',  # german
    u'belly',  # english
    u'brzucha',  # polish
    u'buik',  # dutch
    u'břišní',  # czech
    u'buric',  # romanian
    u'mag',  # swedish
    u'mage',  # norwegian
    u'mave',  # danish
    u'ventre',  # italian
    u'vientre',  # spanish
    u'oryantal',  # turkish
    u'perut',  # malay
    u'pilvo',  # lithuanian
    u'trbušni',  # croatian
    u'vatsa',  # finnish
    u'τηςκοιλιάς',  # greek
    u'восточны\w*',  # russian for 'eastern'
    u'живота',  # russian
    u'стомачен',  # macedonian
    u'בטן',  # hebrew
    u'الشرقي',  # arabic
    u'ระบำหน้าท้อง',  # thai
    u'ベリー',  # japanese
    u'肚皮',  # chinese simplified
    u'배꼽',  # korean
    u'पेट',  # hindi
    u'बेली',  # hindi
)

GOOD_DANCE = Any(
    commutative_connected(Any(BELLY, NON_BELLY_AMBIGUOUS_DANCE), dance_keywords.EASY_DANCE),
    'raqs sharqi',  # romanization of the arabic
    'raqs baladi',  # romanization of the arabic
    # for an explanation of these, see http://www.shira.net/musings/dance-by-any-other-name.htm
    'transnational fusion',
    commutative_connected(Any(u'tribal'), Any(u'fusi[oó]n\w*')),
    'bellycraft',
    'bellyfit',
    'its unmata',  # ITS unmata
    'american tribal style',
)

RELATED_KEYWORDS = Any(
    'amy sigil',
    'unmata',
    'modern fusion',
    'isolat\w+',
    'sufi',
    'worldbellydancealliance',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
    AMBIGUOUS_DANCE = NON_BELLY_AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BELLY'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'bauch tanz',
            u'ריקודי בטן',
            u'肚皮',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'belly dance',
            'oriental dance',
            'egyptian dance',
            'middle eastern dance',
            'rasq sharqi',
            'tribal fusion',
            u'ベリーダンス',
            u'شرقي‎',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
