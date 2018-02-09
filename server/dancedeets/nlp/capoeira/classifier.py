# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import grammar
from ..street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

CAPOEIRA = Any(
    commutative_connected(Any('capoeira'), Any('angola')),
    commutative_connected(Any('capoeira'), Any('regional')),
    commutative_connected(Any('capoeira'), Any('contemp\w+')),
    'capoeiristas?',
    'capoeira',
)

EVENT = Any(
    keywords.CLASS,
    keywords.PERFORMANCE,
    'rodas?',
    'encontro',
    'demo',
    'demonstration',
)

KEYWORDS = Any(
    'contra\W?mestre',
    'c\.mestres',
    'mestres?',
    'rodas?',
    'encontro',
    'rencontre',
)

OBVIOUS_KEYWORDS = Any(
    u'grupo axé capoeira',
    'grupo capoeira brasil',
    'international capoeira angola foundation',
    'fundacao international de capoeira de angola',
    'world capoeira federation',
)

CAP_EVENT = commutative_connected(CAPOEIRA, EVENT)

CAP_CLASS = commutative_connected(CAPOEIRA, Any('adult', 'kids?', 'beginner', 'mixed\W?level', 'intermediate'))


def is_capoeira_event(classified_event):
    result = is_basic_capoeira_event(classified_event)
    if result[0]:
        return result

    result = is_capoeira_class(classified_event)
    if result[0]:
        return result

    result = has_capoeira_keywords(classified_event)
    if result[0]:
        return result

    result = has_capoeira_organizer(classified_event)
    if result[0]:
        return result

    return result


def has_capoeira_organizer(classified_event):
    org_name = classified_event.fb_event['info'].get('owner', {}).get('name', '').lower()
    if 'capoeira' in org_name:
        return (True, 'Found capoeira in organization name: %s' % org_name, event_types.VERTICALS.CAPOEIRA)

    return (False, '', [])


def has_capoeira_keywords(classified_event):
    cap = classified_event.processed_text.get_tokens(CAPOEIRA)
    keywords = classified_event.processed_text.get_tokens(KEYWORDS)
    if cap and keywords:
        return (True, 'Found capoeira (%s) event with keywords: %s' % (cap, keywords), event_types.VERTICALS.CAPOEIRA)

    cap_keywords = classified_event.processed_text.get_tokens(OBVIOUS_KEYWORDS)
    if cap_keywords:
        return (True, 'Found obvious capoeira keywords: %s' % cap_keywords, event_types.VERTICALS.CAPOEIRA)

    return (False, '', [])


def is_basic_capoeira_event(classified_event):
    cap_event = classified_event.processed_text.get_tokens(CAP_EVENT)
    if cap_event:
        return (True, 'Found capoeira event: %s' % cap_event, event_types.VERTICALS.CAPOEIRA)

    return (False, '', [])


def is_capoeira_class(classified_event):
    cap_event = classified_event.processed_text.get_tokens(CAP_CLASS)
    if cap_event:
        return (True, 'Found capoeira event: %s' % cap_event, event_types.VERTICALS.CAPOEIRA)

    return (False, '', [])
