# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

CAPOEIRA_WORD = Any(
    'capoeira\w*',
    u'巴西戰舞',  # chinese capoeira
    u'卡波耶拉',  # chinese capoeira
    u'카포에라',  # korean capoeira
)

CAPOEIRA = Name(
    'CAPOEIRA',
    Any(
        commutative_connected(CAPOEIRA_WORD, Any('angola')),
        commutative_connected(CAPOEIRA_WORD, Any('regional')),
        commutative_connected(CAPOEIRA_WORD, Any('contemp\w+')),
        CAPOEIRA_WORD,
        'capoeiristas?',
        u'maculel[êe]',
    )
)

EVENT = Any(
    'rodas?',
    'encontro',
    'demo',
    'demonstration',
    'seminar',
    'rencontre',
)

KEYWORDS = Any(
    'contra\W?mestre',
    'c\.mestres',
    'mestres?',
)

OBVIOUS_KEYWORDS = Any(
    u'grupo axé capoeira',
    'grupo capoeira brasil',
    'international capoeira angola foundation',
    'fundacao international de capoeira de angola',
    'world capoeira federation',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = CAPOEIRA
    ADDITIONAL_EVENT_TYPE = EVENT
    GOOD_KEYWORDS = OBVIOUS_KEYWORDS, KEYWORDS

    def _quick_is_dance_event(self):
        return self._has(CAPOEIRA)

    def is_dance_event(self):
        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        result = self.has_capoeira_keywords()
        if result:
            return result

        return False

    @base_auto_classifier.log_to_bucket('has_capoeira_keywords')
    def has_capoeira_keywords(self):
        if self._get(CAPOEIRA) and self._get(KEYWORDS):
            return 'Found capoeira event with keywords'

        if self._get(OBVIOUS_KEYWORDS):
            return 'Found obvious capoeira keywords'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'CAPOEIRA'

    @classmethod
    def get_rare_search_keywords(cls):
        return []

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'capoeira',
            'capoeira angola',
            'capoeira regional',
            'capoeira contemporânea',
            'capoeira roda',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return [
            'roda',
            'encontro',
            'demo',
            'demonstration',
            'recontre',
        ]

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return CAPOEIRA
