# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    'country\W?line',
    u'カントリーライン',
    commutative_connected(Any(
        'square',
        'barn',
    ), keywords.EASY_DANCE),
    '(?:country\W?(?:and|&|\+)?\W?western|c\Ww|texas|rhythm|double|night\W?club)\W?(?:two|2)\W?step',
    'contra\W?barn',
    'deux\W?temp',
    'texas shuffle step\w*',
    '(?:two|2)\W?step\w*',
    'clogging',
    'contredanse',
    'contra\W?danc\w+',
)

LINE_DANCE = commutative_connected(Any(
    'line',
    u'ライン',
), keywords.EASY_DANCE)

AMBIGUOUS_DANCE = Any(
    'country',
    u'カントリー',
    'c\Ww',
    'cowboy',
    u'カウボーイ',
    'traveling cha\W?cha',
    'polka (?:ten|10)\W?step',
    'modern\W?western',
    'modern\W?western\W?square',
    'western\W?square',
    'american\W?square',
    'square',
    u'スクエア',
    'mwsd',
    'clog',
    'contradanza',
)

GOOD_KEYWORDS = Any(
    'ucwdc',
    'united country western dance council',
    'cwdi',
    'country western dance international',
)


class CountryClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.COUNTRY

    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'social',
        'convention',
        'festival',
        'marathon',
    )

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(CountryClassifier, self).is_dance_event()
        if result:
            return result

        result = self.is_line_dance()
        if result:
            return result

        return False

    def is_line_dance(self):
        if self._title_has(LINE_DANCE) and self._title_has(self.AMBIGUOUS_DANCE):
            return 'title has line dance'

        return False


def is_country_event(classified_event):
    classifier = CountryClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
