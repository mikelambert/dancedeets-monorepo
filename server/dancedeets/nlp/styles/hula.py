# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import hulahoop

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

JA_HULA = Any(u'フラ')

JA_HULA_KEYWORDS = Any(
    u'hula',
    u'hawaii\w*',
    u'ハワイ',
    u'aloha',
    u'アロハ',
    u'ohana',
    u'オハナ',
    # Don't include ダンス, as that applies to フラメンコ too
)

HULA = Any(
    u'hula',  # english
    u'χούλα',  # greek
    u'хула',  # macedonian
    u'החולה',  # hebrew
    u'حولا',  # arabic
    u'ฮูลา',  # thai
    u'フラ',  # japanese
    u'呼啦',  # chinese simplified
    u'훌라',  # korean
)

TAHITIAN = Any(
    u'tahiti\w*',  # polish
    u'таитянского',  # russian
    u'тахитски',  # macedonian
    u'טאהיטיאן',  # hebrew
    u'تاهيتي',  # arabic
    u'ชาวทาฮีตี',  # thai
    u'タヒチアン',  # japanese
    u'大溪地',  # chinese simplified
    u'타히티',  # korean
)

HAWAIIAN = Any(
    u'ha[vw]a[iïj]\w*',
    u'χαβάης',  # greek
    u'гавайски\w*',  # russian
    u'хавајски',  # macedonian
    u'הוואי',  # hebrew
    u'هاواي',  # arabic
    u'ฮาวาย',  # thai
    u'ハワイアン',  # japanese
    u'夏威夷',  # chinese simplified
    u'하와이',  # korean
)

# Polynesian dance encompasses Tahitian, Tongan, Samoan, Fijian, Maori (New Zealand) and Hawaiian styles

POLYNESIAN = Any(
    u'pol[iy]n[eé][sz]\w+'
    u'πολυνησιακό',  # greek
    u'полинезий?ски\w*',  # russian
    u'פולינזי',  # hebrew
    u'البولينيزية',  # arabic
    u'โพลินีเชีย',  # thai
    u'ポリネシアン',  # japanese
    u'波利尼西亚',  # chinese simplified
    u'波利尼西亞',  # chinese traditional
    u'폴리네시아 인',  # korean
)

LUAU = Any(
    u'luau',
    u'ルアウ',  # japanese
    u'루아 ?우',  # korean
)

GOOD_DANCE = Any(
    HULA,
    u'kahiko hula',
    u'ori tahiti',
)
AMBIGUOUS_DANCE = Any(
    u'ori',
    TAHITIAN,
    POLYNESIAN,
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = GOOD_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = LUAU
    GOOD_BAD_PAIRINGS = [
        (HULA, hulahoop.HULAHOOP),
    ]

    @base_auto_classifier.log_to_bucket('quick_is_dance_event')
    def _quick_is_dance_event(self):
        # Turns out フラ without \b is too common.
        # It matches フランス, フランク, and more...
        # So if we have フラ, ensure we have other hula-esque keywords.
        if self._has(JA_HULA):
            if self._has(JA_HULA_KEYWORDS):
                return True
            else:
                return False
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'HULA'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'フラ',
            u'ハワイアンダンス',
            u'ポリネシアン',
            u'大溪地',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'hula',
            u'hula dance',
            u'tahitian dance',
            u'ori',
            u'ori tahiti',
            u'hawaiian dance',
            u'polynesian',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return ['luau']

    @classmethod
    def _get_classifier(cls):
        return Classifier
