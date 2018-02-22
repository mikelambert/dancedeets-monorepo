# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..street import keywords

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

CAP_EVENT = commutative_connected(CAPOEIRA, EVENT)

CAP_CLASS = commutative_connected(CAPOEIRA, keywords.CLASS_LEVELS)


class CapoeiraClassifier(base_auto_classifier.DanceStyleEventClassifier):
    __metaclass__ = base_auto_classifier.AutoRuleGenerator

    vertical = event_types.VERTICALS.CAPOEIRA

    GOOD_DANCE = CAPOEIRA
    ADDITIONAL_EVENT_TYPE = EVENT
    GOOD_KEYWORDS = OBVIOUS_KEYWORDS, KEYWORDS

    def _quick_is_dance_event(self):
        return self._has(CAPOEIRA)


def is_capoeira_event(classified_event):
    result = has_capoeira_keywords(classified_event)
    if result[0]:
        return result

    classifier = CapoeiraClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical


def has_capoeira_keywords(classified_event):
    cap = classified_event.processed_text.get_tokens(CAPOEIRA)
    keywords = classified_event.processed_text.get_tokens(KEYWORDS)
    if cap and keywords:
        return (True, 'Found capoeira (%s) event with keywords: %s' % (cap, keywords), event_types.VERTICALS.CAPOEIRA)

    cap_keywords = classified_event.processed_text.get_tokens(OBVIOUS_KEYWORDS)
    if cap_keywords:
        return (True, 'Found obvious capoeira keywords: %s' % cap_keywords, event_types.VERTICALS.CAPOEIRA)

    return (False, '', [])
