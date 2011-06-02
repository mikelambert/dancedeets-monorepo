# -*-*- encoding: utf-8 -*-*-

import logging
import re
from spitfire.runtime.filters import skip_filter

# TODO: translate to english before we try to apply the keyword matches
# TODO: if event creator has created dance events previously, give it some weight
# TODO: add keyword matches for dance crews, popular dance names
# TODO: 

# TODO: for each style-keyword, give it some weight. don't be a requirement but yet-another-bayes-input
# TODO: add a bunch of classifier logic

# maybe feed keywords into auto-classifying event type? bleh.

easy_dance_keywords = [
    'dances?', 'dancing', 'dancers?',
    'punking', 'punkers?', 
    'funk', 'hip.?hop', 'punk',
    # french
    'danser', 'robots?', 
]
dance_keywords = [
    'street.?dance', 'break.?dance', 'break.?dancing?',
    'turf(?:ing)?', 'flex(?:ing)?', 'bucking?', 'jooking?',
    'b.?boys?', 'b.?boying?', 'b.?girls?', 'b.?girling?', 'breaks', 'breaking?', 'breakers?', 'power.?moves?', 'footwork', 'footworking?',
    'top.?rock(?:ers?|ing|)', 'up.?rock(?:ers?|ing|)',
    'housers?', 'house ?danc\w*',
    'lockers?', 'locking?', 'lock dance',
    'wh?aa?cc?kers?', 'wh?aa?cc?king?', 'wh?aa?cc?k',
    'poppers?', 'popp?ing?',
    'hitting',
    'waving?', 'wavers?',
    'isolation', 'robott?ing?',
    'strutters?', 'strutting',
    'glides?', 'gliding', 
    'boogaloo',
    'tuts?', 'tutting?', 'tutters?',
    'n(?:ew|u).?styles?', 'all.?style[zs]?', 'mix(?:ed)?.?style[sz]?'
    'me against the music',
    'krump', 'krumping?',
    'choreograph(?:y|ed)', 'choreographers?', 'choreo', 'street jazz', 'street funk', 'jazz funk',
    'new jack swing', 'hype danc\w*', '90.?s hip.?hop', 'social hip.?hop', 'old school hip.?hop',
    'hype',
    'vogue', 'voguers?', 'vogue?ing',
]

easy_event_keywords = [
    'jams?', 'club', 'shows?', 'performances?', 'contests?',
    'sessions?',
    'stages?',
]

event_keywords = [
    'boty', 'competitions?', 'battles?', 'tournaments?', 'judge[sz]?', 'jury', 'preselection',
    r'\d+[ -]?(?:vs?\.?|x|×|on)[ -]?\d+',
    r'(?:seven|7)\W+(?:to|two|2)\W+smoke',
    'cyphers?',
    'workshops?', 'class with', 'master class(?:es)?', 'auditions?', 'try.?outs?', 'class(?:es)?',
    'cours',
    'abdc',
]

easy_dance_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(easy_dance_keywords))
easy_event_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(easy_event_keywords))
dance_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(dance_keywords))
event_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(event_keywords))

capturing_keyword_regex = re.compile(r'(?i)\b(%s)\b' % '|'.join(easy_dance_keywords + easy_event_keywords + dance_keywords + event_keywords))

# NOTE: Eventually we can extend this with more intelligent heuristics, trained models, etc, based on multiple keyword weights, names of teachers and crews and whatnot

def is_dance_event(fb_event):
    if 'name' not in fb_event['info']:
        logging.info("fb event id is %s has no name, with value %s", fb_event['info']['id'], fb_event)
        return False
    search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
    easy_dance_matches = set(easy_dance_regex.findall(search_text))
    easy_event_matches = set(easy_event_regex.findall(search_text))
    dance_matches = set(dance_regex.findall(search_text))
    event_matches = set(event_regex.findall(search_text))
    if (
            # one critical dance keyword and at least some event-y kind of keyword
            (len(dance_matches) >= 1 and len(event_matches) + len(easy_event_matches) >= 1) or
            # one critical event and at least some dance-y kind of keyword
            (len(event_matches) >= 1 and len(dance_matches) + len(easy_dance_matches) >= 1)
        ):
        return dance_matches.union(easy_dance_matches), event_matches.union(easy_event_matches)
    else:
        return False

@skip_filter
def highlight_keywords(text):
    return capturing_keyword_regex.sub('<span class="matched-text">\\1</span>', text)
