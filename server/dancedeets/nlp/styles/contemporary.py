# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballet

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

TECHNIQUES = Any(
    'limon',
    'hawkins',
    'cunningham',
    'release',
    'alexander',
    'taylor',
    'humphrey-weidman',
)

CONTEMPORARY = Any(
    u'contemp',
    u'contempor\w+',
    u'kontemporaryong',  # tagalog
    u'kortárs',  # hungarian
    u'nutidig',  # danish
    u'nykytanssi',  # finnish
    u'súčasný',  # contemporary slovak
    u'současný',  # czech
    u'suvremeni',  # croatian
    u'współczesn\w+',  # polish
    u'kontemporari',  # malay
    u'zeitgenössischer',  # german
    u'çağdaş',  # turkish
    u'đương đại',  # vietnamese
    u'šiuolaikinis',  # lithuanian
    u'σύγχρονο',  # greek
    u'современ\w*',  # macedonian
    u'контепорари',  # russian
    u'עכשווי',  # hebrew
    u'المعاصر',  # arabic
    u'การเต้นร่วมสมัย',  # thai
    u'コンテンポラリー',  # japanese
)

REAL_DANCE = Any(
    commutative_connected(CONTEMPORARY, ballet.BALLET),
    connected(TECHNIQUES, Any('techniques?')),
)

AMBIGUOUS_DANCE = CONTEMPORARY


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    REAL_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        u'recital',
        u'gala',
        u'ガラ',
    )

    @classmethod
    def finalize_class(cls, other_style_regexes):
        # Don't allow "modern jazz", "modern bachata", etc to count as modern
        cls.GOOD_BAD_PAIRINGS = [
            (Any(u'šiuolaikinis'), Any(
                u'nails?',
                u'nagų\w*',
                u'paznokci\w*',
            )),
            (CONTEMPORARY, Any(commutative_connected(CONTEMPORARY, Any(*other_style_regexes)),)),
        ]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'CONTEMPORARY'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'contemp dance',
            u'kortárs tánc',
            u'nykytanssi',
            u'současný',
            u'współczesny',
            u'芭蕾',
            u'современный танец',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'contemp',
            u'contemporary',
            u'contemporary dance',
            u'contemporaine',
            u'contemporanea',
            u'zeitgenössischer',
            u'çağdaş',
            u'σύγχρονο',
            u'современный',
            u'コンテンポラリー',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
