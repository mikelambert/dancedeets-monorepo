# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

CLASSICAL = Any(
    u'[ck]l[aá]ss?z?i[cčkq]\w*',
    u'klassieke',  # dutch
    u'klassis\w+',
    u'klassista',  # finnish
    u'klasszik\w+',  # hungarian
    u'klasyc\w+',  # polish
    u'cổ điển',  # vietnamese
    u'ινδικό',  # greek
    u'клас?иче\w+',  # russian/macedonian
    u'קלאסי',  # hebrew
    u'التقليدي',  # arabic
    u'โบราณ',  # thai
    u'古典',  # chinese
    u'고전',  # korean
)
INDIAN = Any(
    u'indian',  # tagalog
    u'indienne',  # french
    u'india',  # spanish
    u'indiana',  # italian
    u'indický',  # czech
    u'hint',  # turkish
    u'indų',  # lithuanian
    u'indijski',  # croatian
    u'indiase',  # dutch
    u'indischer',  # german
    u'indian',  # danish
    u'indisk',  # norwegian
    u'intialaista',  # finnish
    u'indiai',  # hungarian
    u'indyjski',  # polish
    u'ấn độ',  # vietnamese
    u'κλασικό',  # greek
    u'индий?ски\w*',  # russian/macedonian
    u'הודי',  # hebrew
    u'الهندي',  # arabic
    u'แบบอินเดีย',  # thai
    u'印度',  # chinese
    u'インディアン',  # japanese
    u'인도',  # korean
)
CLASSICAL_INDIAN = commutative_connected(CLASSICAL, INDIAN)

CLASSICAL_DANCES = [
    u'bharata',
    u'natyam',
    u'kathak',
    u'kathakali',
    u'kuchipudi',
    u'manipuri',
    u'mohiniyattam',
    u'mohiniattam',
    u'odissi',
    u'sattriya',
    u'nataraja',
    u'tandava',
    u'rasa',
    u'lila',
    u'lasya',
]
DIVINE_DANCES = [
    u'nataraja',
    u'tandava ',
    u'rasa ',
    u'lila',
    u'lasya',
]

FOLK_DANCES = [
    u'bihu',
    u'bagurumba',
    # u'bhangra',
    u'chang',
    u'cheraw',
    u'chhau',
    u'dollu',
    u'kunitha',
    u'giddha',
    u'garba',
    u'dandiya',
    u'raas',
    u'ghoomar',
    u'ghumura',
    u'kachhi',
    u'ghodi',
    u'karma',
    u'lavani',
    u'saang',
    # u'sword',
    # u'dance',
    u'tippani',
    u'yakshagana',
]

OTHER_DANCES = [
    u'kalbeliya',
    u'bhawai',
    u'teratali',
    u'ghumar',
    u'kirtan',
]

DANCE_NAMES = CLASSICAL_DANCES + DIVINE_DANCES + FOLK_DANCES + OTHER_DANCES
AMBIGUOUS_DANCE = Any(CLASSICAL_INDIAN, *DANCE_NAMES)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'INDIAN'

    @classmethod
    def get_rare_search_keywords(cls):
        return DANCE_NAMES + [x + ' dance' for x in DANCE_NAMES]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'indian dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_DANCE)
