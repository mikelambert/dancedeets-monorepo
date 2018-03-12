# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

JAZZ = Any(
    u'jazz',
    u"ג'אז",  # hebrew
    u'caz',  # turkish
    u'džiazo',  # lithuanian
    u'jazzo[vw]\w+',  # czech
    u'τζαζ',  # greek
    u'джаз\w+',  # russian
    u'джазовый',  # russian
    u'џез',  # macedonian
    u'الجاز',  # arabic
    u'แจ๊ส',  # thai
    u'ジャズ',  # japanese
    u'爵士',  # chinese simplified
    u'재즈',  # korean
)
AMBIGUOUS_DANCE = JAZZ


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(u'recital',)
    GOOD_BAD_PAIRINGS = [(
        JAZZ,
        Any(
            u'vintage',  # vintage jazz!
            u'ensemble',
            u'bossa nova',
            u'blues',
            u'jazz standards',
            u'bebop',
            u'free\Wjazz',
            u'jazz music',
            u'cotton\W?club',
            u'concert',
            u'musicians?',
            u'jazz\W?festival',
            u'jam\W?sessions?',
            u'drums?',
            u'double\W+bass',
            u'trios?',
            u'quartets?',
            u'quintets?',
            u'ensembles?',
            # artists
            u'armstrong',
            u'bille holiday',
            u'chet baker',
            u'coltrane',
            u'duke ellington',
            u'ellington\w*',
            u'etta james',
            u'john coltrane',
            u'louis armstrong',
            u'miles davis',
            u'ray charles',
            u'stan getz',
        )
    )]

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'JAZZ'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'dança de jazz',
            u'taniec jazzowy',
            u'ジャズダンス',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            u'jazz',
            u'jazz dance',
            u'danza jazz',
            u'jazz dans',
            u'jazz tanz',
            u'jazz tánc',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier
