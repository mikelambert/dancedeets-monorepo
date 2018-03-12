# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

THEATER = Any(
    u'divade?l\w*',  # czech
    u'kazališt\w*',  # croatian
    u'th?[eé][aâ]te?r\w*',
    u'tiyatr\w+',  # turkish
    u'teatter\w+',  # finnish
    u'θεάτρ\w*',  # greek
    u'театар\w+',  # macedonian
    u'театра\w+',  # macedonian
    u'תיאטר\w*',  # hebrew
    u'المسرح\w*',  # arabic
    u'ละคร\w*',  # thai
    u'劇場',  # japanese
    u'剧院',  # chinese simplified
    u'劇院',  # chinese traditional
    u'戏剧',  # chinese simplified
    u'戲劇',  # chinese traditional
    u'演劇',  # japanese
    u'剧',  # chinese simplified
    u'劇',  # chinese traditional
    u'극장',  # korean
    u'연극',  # korean
)

MUSICAL = Any(
    u'glazben\w*',  # croatian
    u'hudebn\w*',  # czech
    u'kazališ\w+',  # croatian
    u'm[uü][sz][iy][ck]\w*',
    u'muziek\w*',  # dutch
    u'színház\w*',  # hungarian
    u'μουσικ\w+',  # greek
    u'музичк\w*',
    u'музык\w+',
    u'מוסיקלי',  # hebrew
    u'الموسيقي',  # arabic
    u'ดนตรี',  # thai
    u'ミュージカル',  # japanese
    u'音乐',  # chinese simplified
    u'音樂',  # chinese traditional
    u'뮤지컬',  # korean
)

REAL_DANCE = Any(
    u'múa hát',  # vietnamese musical dance
    u'nhà hát nhạc kịch',  # vietnamese musical theater
    commutative_connected(MUSICAL, THEATER),
    commutative_connected(THEATER, dance_keywords.EASY_DANCE),
    'broadway dance',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = REAL_DANCE
    ADDITIONAL_EVENT_TYPE = Any(u'recital',)
    GOOD_BAD_PAIRINGS = [
        (Any('broadway dance'), Any('broadway dance center')),
    ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'MUSICAL_THEATER'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'danse de théâtre',  # french
            u'danse théâtrale',  # french
            u'danza del teatro',  # spanish
            u'danza teatral',  # spanish
            u'danza teatrale',  # italian
            u'dança de teatro',  # portuguese
            u'dança teatral',  # portuguese
            u'divadelní tanec',  # czech
            u'glazbeno kazalište',  # croatian
            u'hudební divadlo',  # czech
            u'kazališni ples',  # croatian
            u'musical theater',  # english
            u'musiikkiteatteri',  # finnish
            u'musikal teatro',  # tagalog
            u'musikalsk teater',  # norwegian
            u'musikteater',  # swedish
            u'musiktheater',  # german
            u'muziek theater',  # dutch
            u'muzikinis teatras',  # lithuanian
            u'múa hát',  # vietnamese
            u'müzikal tiyatro',  # turkish
            u'nhà hát nhạc kịch',  # vietnamese
            u'nhảy múa',  # vietnamese
            u'színházi tánc',  # hungarian
            u'taniec teatralny',  # polish
            u'tarian teater',  # malay
            u'teater muzik',  # malay
            u'teaterdans',  # swedish
            u'teatr muzyczny',  # polish
            u'teatralsk dans',  # norwegian
            u'teatro musical',  # portuguese
            u'teatro musicale',  # italian
            u'teatro sayaw',  # tagalog
            u'teatro šokis',  # lithuanian
            u'teatru dans',  # romanian
            u'teatru muzical',  # romanian
            u'teatteri-tanssi',  # finnish
            u'teatteritanssi',  # finnish
            u'theater dance',  # english
            u'theater dans',  # dutch
            u'theater tanz',  # german
            u'theatertanz',  # german
            u'theatrale dans',  # dutch
            u'theatre musical',  # french
            u'theatrical dance',  # tagalog
            u'tiyatro dansı',  # turkish
            u'zenei színház',  # hungarian
            u'θεατρικό χορό',  # greek
            u'μουσικό θέατρο',  # greek
            u'χορός θεάτρου',  # greek
            u'музички театар',  # macedonian
            u'музыкальный театр',  # russian
            u'театарски танц',  # macedonian
            u'театральный танец',  # russian
            u'ריקוד תיאטרון',  # hebrew
            u'ריקוד תיאטרלי',  # hebrew
            u'תיאטרון מוסיקלי',  # hebrew
            u'الرقص المسرح',  # arabic
            u'الرقص المسرحي',  # arabic
            u'المسرح الموسيقي',  # arabic
            u'การแสดงนาฏศิลป์',  # thai
            u'การแสดงละครเวที',  # thai
            u'โรงละครดนตรี',  # thai
            u'ミュージカル劇場',  # japanese
            u'剧院舞蹈',  # chinese simplified
            u'劇院舞蹈',  # chinese traditional
            u'戏剧舞蹈',  # chinese simplified
            u'戲劇舞蹈',  # chinese traditional
            u'演劇舞踊',  # japanese
            u'音乐剧',  # chinese simplified
            u'音樂劇',  # chinese traditional
            u'뮤지컬 극장',  # korean
            u'연극 춤',  # korean
            u'연극',  # korean
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'theatrical dance',
            u'theater dance',
            u'musical theater',
            u'broadway dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
