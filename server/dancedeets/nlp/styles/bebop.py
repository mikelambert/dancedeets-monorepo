# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

BEBOP = Any(
    u'be\W?bop',
    u'бибоп',  # russian
    u'البيبوب',  # arabic
    u'ビバップ',  # japanese
    u'波普',  # chinese simplified, chinese traditional
    u'비밥',  # korean
)
JAZZ_ROCK = Any(
    u"ג'אז רוק",  # hebrew
    u'caz rock',  # turkish
    u'jazz\W?rock',
    u'jazzová skála',  # czech
    u'jazzrock',  # german
    u'τζαζ\W?ροκ',  # greek
    u'джаз\W?рок',  # russian
    u'џез\W?рок',  # macedonian
    u'موسيقى الجاز',  # arabic
    u'ร็อคแจ๊ส',  # thai
    u'ジャズ.?ロック',  # japanese
    u'爵士乐摇滚',  # chinese simplified
    u'爵士樂搖滾',  # chinese traditional
    u'재즈 ?록',  # korean
)
JAZZ_FUSION = Any(
    u"פיוז'ן ג'אז",  # hebrew
    u'caz füzyonu',  # turkish
    u'džiazo sintezė',  # lithuanian
    u'fusione jazz',  # italian
    u'fusión de jazz',  # spanish
    u'fusão jazz',  # portuguese
    u'jazz fusion',
    u'jazz fuzija',  # croatian
    u'jazz fúzió',  # hungarian
    u'jazzfusion',  # swedish
    u'jazzfuusio',  # finnish
    u'jazzová fúze',  # czech
    u'jazzowa fuzja',  # polish
    u'τζαζ σύντηξη',  # greek
    u'джазовый фьюжн',  # russian
    u'џез фузија',  # macedonian
    u'اندماج الجاز',  # arabic
    u'ฟิวชั่นแจ๊ส',  # thai
    u'ジャズフュージョン',  # japanese
    u'爵士融合',  # chinese simplified, chinese traditional
    u'재즈 ?융합',  # korean
)

STYLES = Any(
    BEBOP,
    JAZZ_ROCK,
    JAZZ_FUSION,
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = STYLES

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BEBOP'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'jazzrock',
            'jazz rock',
            'jazz-rock',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'bebop',
            'uk jazz dance',
            'uk jazz dance',
            'jazz fusion dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.STREET_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
