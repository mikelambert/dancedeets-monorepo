# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import partner

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

BALLROOM_STYLES = Any(
    'waltz',
    'viennese waltz',
    'waltz',
    u'왈츠',  # korean waltz
    u'ワルツ',  # japanese waltz
    'tango',
    'foxtrot',
    'quick\W?step',
    'samba',
    'cha\W?cha',
    'rumba',
    'paso doble',
    'jive',
    'east coast swing',
    'bolero',
    'mambo',
    'country (?:2|two)\W?step',
    'american tango',
)

BALLROOM = Any(
    'ballroom',
    'ballsaal',  # german
    u'tane\w+ sál',  # czech
    'salle de bal',  # french
    u'salón de baile',  # spanish
    'sala balowa',  # polish
    u'бальный',  # russian
    u'phòng khiêu vũ',  # vietnamese
    u'舞廳',
    u'ボールルーム',
    u'사교',
)

BALLROOM_DANCE = commutative_connected(BALLROOM, dance_keywords.EASY_DANCE)
BALLROOM_KEYWORDS = Any(
    BALLROOM_DANCE,
    'dance\W?sport',
    'international ballroom',
    'international latin',
    'american smooth',
    'american rhythm',
    'collegiate ballroom',
    'world dancesport federation',
    'wdsf',
    'world dance council',
    'wdc',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    @classmethod
    def finalize_class(cls, other_style_regex):
        pass

    def is_dance_event(self):
        all_styles = set(self._get(BALLROOM_STYLES))
        all_keywords = set(self._get(BALLROOM_KEYWORDS))

        self._log(
            'ballroom classifier: event %s found styles %s, keywords %s', self._classified_event.fb_event['info']['id'], all_styles,
            all_keywords
        )
        if self._title_has(BALLROOM_DANCE):
            return 'obviously ballroom dance event'

        if len(all_keywords) >= 2:
            return 'Found many ballroom styles'

        if len(all_styles) >= 1 and len(all_keywords) >= 2:
            return 'Found many ballroom styles and keywords'

        if len(all_styles) >= 3:
            return 'Found many ballroom keywords'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BALLROOM'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'ballroom dance',
            'latin ballroom',
            'waltz',
            'viennese waltz',
            'tango',
            'foxtrot',
            'quick step',
            'samba',
            'cha cha',
            'rumba',
            'paso doble',
            'jive',
            'east coast swing',
            'bolero',
            'mambo',
            'country 2 step',
            'american tango',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(BALLROOM_KEYWORDS)
