# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

AMBIGUOUS_DANCE = Any(
    u'afro\W?[ck](?:u|uu|ü)b[aá]\w*',  # malay
    u'αφρο\W?κουβανικά',  # greek
    u'афро\W?кубанск\w+',  # russian
    u'אפרו\W*קובני',  # hebrew
    u'คิวบา',  # thai
    u'アフロキューバン?',  # japanese
    u'非洲裔?\W*古巴',  # chinese simplified
    u'아프리카\W*쿠바',  # korean
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any('festival',)

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'AFRO_CUBAN'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'afro cuba',  # malay
            u'afro cubain',  # french
            u'afro cubaines',  # french
            u'afro cuban',  # english
            u'afro cubano',  # portuguese
            u'afro cubanske',  # danish
            u'afro kubai',  # hungarian
            u'afro kubaner',  # german
            u'afro kubanska',  # croatian
            u'afro kubański',  # polish
            u'afro kubos',  # lithuanian
            u'afro kubánský',  # czech
            u'afro kuubalaisia',  # finnish
            u'afro küba',  # turkish
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return []

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
