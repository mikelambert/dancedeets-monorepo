# -*-*- encoding: utf-8 -*-*-
#

import keywords
import grammar
from grammar import Any
from nlp import event_classifier
from nlp import event_auto_classifier
import styles
import event_types

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
    "pop", # dangerous one due to pop music
)

ANY_LOCK = Any(
    keywords.STYLE_LOCK,
#    "lock\w*",
    u'ロック',
)

# No extras needed here
ANY_WAACK = Any(
    keywords.STYLE_WAACK,
    # we don't want "wake" to trigger, so let's enforce lengthß
    #"[uw]h?aa?c?c?k\w*",
    "[uw]h?aac?c?k\w*",
    "[uw]h?aa?cc?k\w*",
    "punk\w+",
)

ANY_HOUSE = Any(
    keywords.STYLE_HOUSE,
    keywords.HOUSE, # TODO: Rename to STYLE_HOUSE_WEAK,
)

ANY_HIPHOP = Any(
    keywords.STYLE_HIPHOP,
    keywords.STYLE_HIPHOP_WEAK,
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

ANY_LITEFEET = Any(
    keywords.STYLE_LITEFEET,
)

ANY_FLEX = Any(
    keywords.STYLE_FLEX,
)

ANY_BEBOP = Any(
    keywords.STYLE_BEBOP,
    keywords.STYLE_BEBOP_WEAK,
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

STYLES = {
    styles.BREAK: ANY_BREAK,
    styles.POP: ANY_POP,
    styles.LOCK: ANY_LOCK,
    styles.WAACK: ANY_WAACK,
    styles.HOUSE: ANY_HOUSE,
    styles.HIPHOP: ANY_HIPHOP,
    styles.DANCEHALL: ANY_DANCEHALL,
    styles.KRUMP: ANY_KRUMP,
    styles.TURF: ANY_TURF,
    styles.LITEFEET: ANY_LITEFEET,
    styles.FLEX: ANY_FLEX,
    styles.BEBOP: ANY_BEBOP,
    styles.ALLSTYLE: ANY_ALLSTYLE,
    styles.VOGUE: ANY_VOGUE,
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

ANY_PERFORMANCE = Any(
    keywords.PERFORMANCE,
)

ANY_WORKSHOP = Any(
    keywords.CLASS,
)

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

ANY_AUDITION = Any(
    keywords.AUDITION,
)

ANY_REGULAR_CLASS = None#Any(
# Hah, pull this in from studio classes site/subproject
#)

EVENT_TYPES = {
    event_types.BATTLE: ANY_BATTLE,
    event_types.PERFORMANCE: ANY_PERFORMANCE,
    event_types.WORKSHOP: ANY_WORKSHOP,
    event_types.PARTY: ANY_PARTY,
    event_types.SESSION: ANY_SESSION,
    event_types.AUDITION: ANY_AUDITION,
    #event_types.REGULAR_CLASS: ANY_REGULAR_CLASS,
}

BROAD_STYLES = STYLES.copy()
BROAD_STYLES[styles.BREAK] = ANY_BREAK_BROAD


def format_as_search_query(text, broad=True):
    processed_text = event_classifier.StringProcessor(text)
    category_list = EVENT_TYPES.copy()
    category_list.update(BROAD_STYLES if broad else STYLES)
    for category, rule in category_list.iteritems():
        replaced, count = processed_text.replace_with(rule, lambda x: 'categories:%s' % category.index_name)
    return processed_text.text


def find_rules_in_text(text, rule_dict):
    # Eliminate all competitors, before trying to determine the style
    no_competitors_text = event_auto_classifier.find_competitor_list(text)
    if no_competitors_text:
        text = text.replace(no_competitors_text, '')
    found_styles = {}
    for line in text.lower().split('\n'):
        if len(line) > 400:
            continue
        processed_text = event_classifier.StringProcessor(line)
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

def find_rules(fb_event, styles):
    name = fb_event['info'].get('name', '').lower()
    name = name.replace('freestyle session', 'fs')
    found_styles = find_rules_in_text(name, styles)
    if not found_styles:
        found_styles = find_rules_in_text(fb_event['info'].get('description', '').lower(), styles)
    return found_styles

def find_styles(fb_event):
    return find_rules(fb_event, BROAD_STYLES)

def find_event_types(fb_event):
    return find_rules(fb_event, EVENT_TYPES)
