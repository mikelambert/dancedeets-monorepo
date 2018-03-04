# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import partner

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

WALTZ_KEYWORDS = [
    u'keringő',  # hungarian
    u'valcer',  # croatian
    # too popular
    # u'vals',  # romanian
    u'valsa',  # portuguese
    u'valsas',  # lithuanian
    u'valse',  # french
    u'valssi',  # finnish
    u'valzer',  # italian
    u'valčík',  # czech
    u'walc',  # polish
    # too popular
    # u'wals',  # dutch
    u'walzer',  # german
    u'βάλς',  # greek
    u'валцер',  # macedonian
    u'вальс',  # russian
    u'ואלס',  # hebrew
    u'ואלס אנגלי',  # hebrew
    u'ואלס וינאי',  # hebrew
    u'الفالس',  # arabic
    u'เพลงเต้นรำ',  # thai
    u'ワルツ',  # japanese
    u'华尔兹',  # chinese simplified
    u'華爾茲',  # chinese traditional
    u'왈츠',  # korean
]
GOOD_DANCE = Any(*WALTZ_KEYWORDS)

AMBIGUOUS_WORDS = Any('NOTHEIRNGEIRGNE')


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    AMBIGUOUS_DANCE = AMBIGUOUS_WORDS
    GOOD_DANCE = GOOD_DANCE

    def _quick_is_dance_event(self):
        result = ballroom.Style.get_classifier()(self._classified_event).is_dance_event()
        if result:
            return False
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'WALTZ'

    @classmethod
    def get_rare_search_keywords(cls):
        return WALTZ_KEYWORDS

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'waltz',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return partner.EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(AMBIGUOUS_WORDS, GOOD_DANCE)
