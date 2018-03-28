# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import ballroom_keywords
from dancedeets.nlp import event_types

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

SAMBA_KEYWORDS = Any(
    *[
        u'samba no p[ée]',
        u'samba de gafieira',
        u'samba pagode',
        u'samba ax[ée]',
        u'samba\W?rock',
        u'samba de roda',
        u'roda de samba',
    ] + ballroom_keywords.SAMBA
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = SAMBA_KEYWORDS

    def _quick_is_dance_event(self):
        ballroom_classifier = ballroom.Style.get_classifier()(self._classified_event, debug=self._debug)
        result = ballroom_classifier.is_dance_event()
        for log in ballroom_classifier.debug_info():
            self._log(log)
        if result:
            return False
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'SAMBA'

    @classmethod
    def get_rare_search_keywords(cls):
        return ballroom_keywords.SAMBA

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'samba',
            'samba de gafieira',
            'samba pagode',
            'samba',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
