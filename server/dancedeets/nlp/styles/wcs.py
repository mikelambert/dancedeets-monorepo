# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import partner
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

PROFESSIONALS = grammar.FileBackedKeyword('../styles/wcs_dancers')

WEST_COAST_SWING = Any('west coast swing\w*', PROFESSIONALS)

WCS = Any('wcs')

WESTIES = Any('westies?')

WCS_BASICS = Any(
    'sugar push',
    'sugar tuck',
    'left side pass',
    'under arm',
    'whip',
)

AMBIGUOUS_WORDS = Any(WCS, WESTIES)

# Event Sites:
# https://www.worldsdc.com/events/


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_WORDS
    GOOD_DANCE = WEST_COAST_SWING
    ADDITIONAL_EVENT_TYPE = Any(
        'festival',
        'marathon',
    )

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        result = self.is_wcs()
        if result:
            return result

        return False

    @base_auto_classifier.log_to_bucket('is_wcs')
    def is_wcs(self):
        if self._title_has(WEST_COAST_SWING):
            return 'has west coast swing title'

        if self._title_has(WESTIES) or self._title_has(WCS):
            if self._has(WEST_COAST_SWING):
                return 'has wcs/westies title, and west coast swing keywords'

            if self._has(WCS_BASICS):
                return 'has wcs/westies title, and wcs keywords'

            if self._has(keywords.EASY_DANCE):
                return 'has wcs/westies title, and dance keywords'

        if self._title_has(WESTIES) and (self._has(WCS) or self._has(WEST_COAST_SWING)):
            return 'has westies title, and wcs keywords'

        if len(list(self._get(WEST_COAST_SWING))) >= 2:
            return 'has two or more names'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'WCS'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'west coast swing',
            'wcs',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(WEST_COAST_SWING, WCS)
