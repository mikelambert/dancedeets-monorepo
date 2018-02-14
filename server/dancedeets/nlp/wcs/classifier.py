# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..ballroom import classifier as ballroom_classifier
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

PROFESSIONALS = grammar.FileBackedKeyword('../wcs/professionals')

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


class WcsClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.WCS

    AMBIGUOUS_DANCE = AMBIGUOUS_WORDS
    GOOD_DANCE = WEST_COAST_SWING
    BAD_DANCE = None

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(WcsClassifier, self).is_dance_event()
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


def is_wcs_event(classified_event):
    classifier = WcsClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
