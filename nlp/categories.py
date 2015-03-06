# -*-*- encoding: utf-8 -*-*-
#

import keywords
import grammar
from grammar import Any
from nlp import event_classifier
from nlp import event_auto_classifier

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
    "[uw]h?aa?c?c?k\w*",
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
    'BREAK': ANY_BREAK,
    'POP': ANY_POP,
    'LOCK': ANY_LOCK,
    'WAACK': ANY_WAACK,
    'HOUSE': ANY_HOUSE,
    'HIPHOP': ANY_HIPHOP,
    'DANCEHALL': ANY_DANCEHALL,
    'KRUMP': ANY_KRUMP,
    'TURF': ANY_TURF,
    'LITEFEET': ANY_LITEFEET,
    'FLEX': ANY_FLEX,
    'BEBOP': ANY_BEBOP,
    'ALLSTYLE': ANY_ALLSTYLE,
    'VOGUE': ANY_VOGUE,
}

BROAD_STYLES = STYLES.copy()
BROAD_STYLES['BREAK'] = ANY_BREAK_BROAD


def format_as_search_query(text, broad=True):
    processed_text = event_classifier.StringProcessor(text)
    styles_list = BROAD_STYLES if broad else STYLES
    for style, rule in styles_list.iteritems():
        replaced, count = processed_text.replace_with(rule, lambda x: 'categories:%s' % style)
    return processed_text.text


def find_styles_in_text(text, broad=True):
    # Eliminate all competitors, before trying to determine the style
    no_competitors_text = event_auto_classifier.find_competitor_list(text)
    if no_competitors_text:
        text = text.replace(no_competitors_text, '')
    styles = {}
    styles_list = BROAD_STYLES if broad else STYLES
    for line in text.lower().split('\n'):
        if len(line) > 400:
            continue
        processed_text = event_classifier.StringProcessor(line)
        processed_text.real_tokenize(keywords.PREPROCESS_REMOVAL)
        # so we can match this with vogue, but not with house
        processed_text.real_tokenize(keywords.HOUSE_OF)
        for style, rule in styles_list.iteritems():
            tokens = processed_text.get_tokens(rule)
            if tokens:
                styles[style] = tokens
    return styles.keys()

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

def find_styles(fb_event):
    styles = find_styles_in_text(fb_event['info'].get('name', ''), broad=True)
    if not styles:
        styles = find_styles_in_text(fb_event['info'].get('description', ''), broad=True)
    return styles
