# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..soulline import classifier as soulline_classifier
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
    '(?:two|2)\W?step\w*',
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

    def __init__(self, classified_event):
        super(CountryClassifier, self).__init__(classified_event)
        self.LINE_DANCE_EVENT = commutative_connected(LINE_DANCE, self.EVENT_TYPE)

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

    @base_auto_classifier.log_to_bucket('is_line_dance')
    def is_line_dance(self):
        if self._title_has(LINE_DANCE) and self._title_has(self.AMBIGUOUS_DANCE):
            return 'title has line dance'

        if self._has(self.LINE_DANCE_EVENT):
            # "Line dance" by itself is good, unless its a soul line dance event
            sl_classifier = soulline_classifier.SoulLineClassifier(self._classified_event)
            if not sl_classifier.is_dance_event():
                return 'body has line dance event'

        return False


def is_country_event(classified_event):
    classifier = CountryClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
