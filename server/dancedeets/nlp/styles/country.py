# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import event_types
from dancedeets.nlp.styles import soulline

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
        'cowboy',
        u'カウボーイ',
    ), dance_keywords.EASY_DANCE),
    '(?:country\W?(?:and|&|\+)?\W?western|c\Ww|texas|rhythm|double|night\W?club)\W?(?:two|2)\W?step',
    'contra\W?barn',
    'deux\W?temp',
    'texas shuffle step\w*',
    'mambo shuffle',
    'triple\W?two\W?step',
)

LINE_DANCE = commutative_connected(Any(
    'line',
    u'ライン',
), dance_keywords.EASY_DANCE)

AMBIGUOUS_DANCE = Any(
    'country',
    u'カントリー',
    'c/w',  # not \W, or 'classi' + 'c w' matches 'classic w/ mark oliver' :/
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
    u'contr[ae]',
)

GOOD_KEYWORDS = Any(
    'ucwdc',
    'united country western dance council',
    'cwdi',
    'country western dance international',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_DANCE
    ADDITIONAL_EVENT_TYPE = Any(
        'social',
        'convention',
        'festival',
        'marathon',
    )

    @classmethod
    def finalize_class(cls, other_style_regexes):
        super(Classifier, cls).finalize_class(other_style_regexes)
        cls.LINE_DANCE_EVENT = commutative_connected(LINE_DANCE, cls.EVENT_TYPE)

    def _quick_is_dance_event(self):
        return True

    def perform_extra_checks(self):
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
            sl_classifier = soulline.Classifier(self._classified_event)
            if not sl_classifier.is_dance_event():
                return 'body has line dance event'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'COUNTRY'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'country western',
            'country dance',
            'barn dance',
            'square dance',
            'country line',
            'contra barn',
            'cowboy dance',
            'two step',
            'c/w dance',
            'western dance',
            'modern western',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.PARTNER_EVENT_TYPESS

    @classmethod
    def get_preprocess_removal(cls):
        return {
            None: Any('square one', 'square 1'),
        }

    @classmethod
    def _get_classifier(cls):
        return Classifier
