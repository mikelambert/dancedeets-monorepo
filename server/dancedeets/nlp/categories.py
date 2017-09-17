# -*-*- encoding: utf-8 -*-*-
#

from .. import event_types
from . import event_classifier
from . import event_structure
from . import keywords
from . import grammar
from .grammar import Any

ANY_BREAK = Any(
    keywords.STYLE_BREAK,
    keywords.STYLE_BREAK_WEAK,
    'break\w*',
)

ANY_BREAK_BROAD = Any(
    ANY_BREAK,
    keywords.BBOY_CREW[grammar.STRONG_WEAK],
    keywords.BBOY_DANCER[grammar.STRONG_WEAK],
)

ANY_POP = Any(
    keywords.STYLE_POP,
    # These two were omitted from the above,
    # since they are not strong enough on their own.
    # But given a dance event, they can be a very strong classifier.
    keywords.STYLE_POP_WEAK,
    #"pop", # dangerous one due to pop music
)

ANY_LOCK_STRICT = Any(
    keywords.STYLE_LOCK,
    #    "lock\w*",
    u'ロック',
)

ANY_LOCK = Any(ANY_LOCK_STRICT,
               #'funk\w*',
               #'funky',
              )

# No extras needed here
ANY_WAACK_STRICT = Any(
    keywords.STYLE_WAACK,
    # we don't want "wake" to trigger, so let's enforce lengthß
    #"[uw]h?aa?c?c?k\w*",
    "[uw]h?aac?c?k\w*",
    "[uw]h?aa?cc?k\w*",
)

ANY_WAACK = Any(
    ANY_WAACK_STRICT,
    "punk\w+",
    #'disco',
)

ANY_HOUSE = Any(
    keywords.STYLE_HOUSE,
    keywords.HOUSE,  # TODO: Rename to STYLE_HOUSE_WEAK,
)

ANY_HIPHOP = Any(
    keywords.STYLE_HIPHOP,
    keywords.STYLE_HIPHOP_WEAK,
    keywords.CHOREO_CREW[grammar.STRONG_WEAK],
    keywords.CHOREO_DANCER[grammar.STRONG_WEAK],
    'hip\Whop\w*',
)

ANY_DANCEHALL = Any(
    keywords.STYLE_DANCEHALL,
    keywords.STYLE_DANCEHALL_WEAK,
)

ANY_KRUMP = Any(
    keywords.STYLE_KRUMP,
    'krump\w*',
)

ANY_TURF = Any(
    keywords.STYLE_TURF,
    'turf\w*',
)

ANY_LITEFEET = Any(keywords.STYLE_LITEFEET,)

ANY_FLEX = Any(
    keywords.STYLE_FLEX,
    keywords.FLEX_KEYWORD[grammar.STRONG_WEAK],
)

ANY_BEBOP = Any(
    keywords.STYLE_BEBOP,
    keywords.STYLE_BEBOP_WEAK,
    keywords.BEBOP_CREW[grammar.STRONG_WEAK],
    'jazz\Wfusion',
)

ANY_ALLSTYLE = Any(
    keywords.STYLE_ALLSTYLE,
    keywords.STYLE_ALLSTYLE_WEAK,
    keywords.FREESTYLE,
    'all\W+style\w+',
)

ANY_VOGUE = Any(
    keywords.VOGUE,
    keywords.EASY_VOGUE,
)

ANY_KIDS = Any(keywords.KIDS,)

STRICT_STYLES = {
    event_types.BREAK: ANY_BREAK,
    event_types.POP: ANY_POP,
    event_types.LOCK: ANY_LOCK_STRICT,
    event_types.WAACK: ANY_WAACK_STRICT,
    event_types.HOUSE: ANY_HOUSE,
    event_types.HIPHOP: ANY_HIPHOP,
    event_types.DANCEHALL: ANY_DANCEHALL,
    event_types.KRUMP: ANY_KRUMP,
    event_types.TURF: ANY_TURF,
    event_types.LITEFEET: ANY_LITEFEET,
    event_types.FLEX: ANY_FLEX,
    event_types.BEBOP: ANY_BEBOP,
    event_types.ALLSTYLE: ANY_ALLSTYLE,
    event_types.VOGUE: ANY_VOGUE,
}

STYLES = {
    event_types.BREAK: ANY_BREAK,
    event_types.POP: ANY_POP,
    event_types.LOCK: ANY_LOCK,
    event_types.WAACK: ANY_WAACK,
    event_types.HOUSE: ANY_HOUSE,
    event_types.HIPHOP: ANY_HIPHOP,
    event_types.DANCEHALL: ANY_DANCEHALL,
    event_types.KRUMP: ANY_KRUMP,
    event_types.TURF: ANY_TURF,
    event_types.LITEFEET: ANY_LITEFEET,
    event_types.FLEX: ANY_FLEX,
    event_types.BEBOP: ANY_BEBOP,
    event_types.ALLSTYLE: ANY_ALLSTYLE,
    event_types.VOGUE: ANY_VOGUE,
    event_types.KIDS: ANY_KIDS,
}

ANY_BATTLE = Any(
    keywords.JUDGE,
    keywords.OBVIOUS_BATTLE,
    keywords.BONNIE_AND_CLYDE,
    keywords.JAM,
    keywords.BATTLE,
    keywords.N_X_N,
    keywords.CONTEST,
)

ANY_PERFORMANCE = Any(keywords.PERFORMANCE,)

ANY_WORKSHOP = Any(keywords.CLASS,)

ANY_PARTY = Any(
    keywords.CYPHER,
    keywords.CLUB_ONLY,
    keywords.JAM,
    keywords.VOGUE,
    keywords.EASY_CLUB,
)

ANY_SESSION = Any(
    keywords.PRACTICE,
    keywords.EASY_SESSION,
)

ANY_AUDITION = Any(keywords.AUDITION,)

EVENT_TYPES = {
    event_types.BATTLE: ANY_BATTLE,
    event_types.PERFORMANCE: ANY_PERFORMANCE,
    event_types.WORKSHOP: ANY_WORKSHOP,
    event_types.PARTY: ANY_PARTY,
    event_types.SESSION: ANY_SESSION,
    event_types.AUDITION: ANY_AUDITION,
}

BROAD_STYLES = STYLES.copy()
BROAD_STYLES[event_types.BREAK] = ANY_BREAK_BROAD


def format_as_search_query(text, broad=True):
    processed_text = event_classifier.StringProcessor(text)
    category_list = EVENT_TYPES.copy()
    category_list.update(BROAD_STYLES if broad else STYLES)
    for category, rule in category_list.iteritems():
        replaced, count = processed_text.replace_with(rule, lambda x: ' categories:%s ' % category.index_name)
    return processed_text.text


def find_rules_in_text(text, rule_dict):
    # Eliminate all competitors, before trying to determine the style
    no_competitors_text = event_structure.find_competitor_list(text)
    if no_competitors_text:
        text = text.replace(no_competitors_text, '')
    found_styles = {}
    # Only grab the first 400 lines
    trimmed_text = '\n'.join(text.lower().split('\n')[:400])
    processed_text = event_classifier.StringProcessor(trimmed_text)
    processed_text.real_tokenize(keywords.PREPROCESS_REMOVAL)
    # so we can match this with vogue, but not with house
    processed_text.real_tokenize(keywords.HOUSE_OF)
    for style, rule in rule_dict.iteritems():
        tokens = processed_text.get_tokens(rule)
        if tokens:
            found_styles[style] = tokens
    return found_styles.keys()


def get_context(fb_event, keywords):
    name = fb_event['info'].get('name', '')
    description = fb_event['info'].get('description', '')
    search_text = (name + ' ' + description).lower()
    import re
    contexts = []
    for keyword in keywords:
        try:
            context_match = re.search(r'.{20}%s.{0,20}' % keyword, search_text, flags=re.DOTALL)
        except re.error:
            raise Exception("Failed to create context-regex for %r" % keyword)
        if context_match:
            contexts.append(context_match.group(0))
        else:
            contexts.append('???????????')
    return contexts


def _name(obj):
    if hasattr(obj, 'name'):  # DBEvent
        return getattr(obj, 'name')
    elif hasattr(obj, 'title'):  # ClassifiedEvent
        return getattr(obj, 'title')
    else:  # FBEvent
        return obj['info'].get('name', '')


def _desc(obj):
    if hasattr(obj, 'description'):  # DBEvent
        return getattr(obj, 'description')
    elif hasattr(obj, 'search_text'):  # ClassifiedEvent
        return getattr(obj, 'search_text')
    else:  # FBEvent
        return obj['info'].get('description', '')


def find_rules(event, styles):
    name = _name(event).lower()
    name = name.replace('freestyle session', 'fs')
    found_styles = find_rules_in_text(name + _desc(event).lower(), styles)
    # Old attempt that prioritized the title:
    # found_styles = find_rules_in_text(name, styles)
    # if not found_styles:
    #     found_styles = find_rules_in_text(_desc(event).lower(), styles)
    return found_styles


def find_styles(event):
    return find_rules(event, BROAD_STYLES)


def find_styles_strict(event):
    return find_rules(event, STRICT_STYLES)


def find_event_types(event):
    return find_rules(event, EVENT_TYPES)
