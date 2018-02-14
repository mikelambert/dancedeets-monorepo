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

REAL_DANCE = Any('west coast swing',)

WCS = Any('wcs')

WCS_BASICS = Any(
    'sugar push',
    'sugar tuck',
    'left side pass',
    'under arm',
    'whip',
)

AMBIGUOUS_WORDS = WCS


class WcsClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.WCS

    AMBIGUOUS_DANCE = AMBIGUOUS_WORDS
    GOOD_DANCE = REAL_DANCE
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

    def is_wcs(self):
        if self._title_has(WCS):
            if self._has(WCS_BASICS):
                return 'has wcs title, and wcs keywords'

            if self._title_has(WCS) and self._has(keywords.EASY_DANCE):
                return 'has wcs title, and dance keywords'

            if self._title_has(WCS) and self._title_has(keywords.EASY_CLUB):
                return 'has wcs title, and party title'
        return False


def is_wcs_event(classified_event):
    classifier = WcsClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
