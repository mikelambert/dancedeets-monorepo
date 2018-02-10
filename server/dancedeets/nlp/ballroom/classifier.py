# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import grammar

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

BALLROOM_STYLES = Any(
    'waltz',
    'viennese waltz',
    'tango',
    'foxtrot',
    'quick\W?step',
    'samba',
    'cha\W?cha',
    'rumba',
    'paso doble',
    'jive',
    'east coast swing',
    'bolero',
    'mambo',
)

BALLROOM_KEYWORDS = Any(
    'dance\W?sport',
    'international ballroom',
    'international latin',
    'american smooth',
    'american rhythm',
    'collegiate ballroom',
    'world dancesport federation',
    'wdsf',
    'world dance council',
    'wdc',
)


def is_ballroom_event(classified_event):
    result = is_many_ballroom_styles(classified_event)
    if result[0]:
        return result

    return result


def is_many_ballroom_styles(classified_event):
    all_styles = classified_event.processed_text.get_tokens(BALLROOM_STYLES)
    all_keywords = classified_event.processed_text.get_tokens(BALLROOM_KEYWORDS)

    if len(set(all_keywords)) >= 4:
        return (True, 'Found many ballroom styles: %s' % all_styles, event_types.VERTICALS.BALLROOM)

    if len(set(all_styles)) >= 1 and len(set(all_keywords)) >= 2:
        return (True, 'Found many ballroom styles (%s) and keywords (%s)' % (all_styles, all_keywords), event_types.VERTICALS.BALLROOM)

    if len(set(all_styles)) >= 3:
        return (True, 'Found many ballroom keywords (%s)' % all_keywords, event_types.VERTICALS.BALLROOM)

    return (False, '', [])
