import logging
import re
from spitfire.runtime.filters import skip_filter

easy_dance_keywords = [
    'dances?', 'dancing', 'dancers?',
    'funk', 'hip.?hop', 'punk',
    # french
    'danser',
]
dance_keywords = [
    'street.?dance',
    'turf(?:ing)?', 'flex(?:ing)?', 'bucking?', 'jooking?',
    'b.?boys?', 'b.?girls?', 'breaks', 'breaking', 'breakers?',
    'top.?rock(?:ers?|ing|)', 'up.?rock(?:ers?|ing|)',
    'housers?', 'house ?danc\w*',
    'lockers?', 'locking?',
    'wh?aackers?', 'wh?aacking?',
    'poppers?', 'popp?ing?', 'hitting',
    'animation', 'isolation', 'robots?',
    'strutters?', 'strutting',
    'glides?', 'gliding', 'waves?', 'waving', 'wavers?',
    'tuts?', 'tutting', 'tutters?',
    'new.?styles?', 'all.?styles?',
    'choreography', 'choreographers?', 'choreo', 'street jazz', 'street funk', 'jazz funk',
    'new jack swing', 'hype danc\w*', '90.?s hip.?hop', 'social hip.?hop', 'old school hip.?hop',
    'hype',
    'w[ha]acking', 'w[ha]ackers?', 'w[ha]ack', 'punking', 'punkers?', 
    'vogue', 'voguers?', 'vogueing',
]

easy_event_keywords = [
    'jams?', 'club', 'shows?', 'performances?', 'contests?',
    'sessions?',
]

event_keywords = [
    'competitions?', 'battles?', 'tournaments?', 'judges?',
    r'\d[ -]?vs?\.?[ -]?\d',
    r'\d ?on ?\d',
    r'(?:seven|7)\W+(?:to|two|2)\W+smoke',
    'cyphers?',
    'workshops?', 'class with', 'master class(?:es)?', 'auditions?', 'try.?outs?', 'class(?:es)?',
    'cours', 'stages?',
    'abdc',
]

easy_dance_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(easy_dance_keywords))
easy_event_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(easy_event_keywords))
dance_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(dance_keywords))
event_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(event_keywords))

capturing_keyword_regex = re.compile(r'(?i)\b(%s)\b' % '|'.join(easy_dance_keywords + easy_event_keywords + dance_keywords + event_keywords))

# NOTE: Eventually we can extend this with more intelligent heuristics, trained models, etc, based on multiple keyword weights, names of teachers and crews and whatnot

def is_dance_event(fb_event):
    search_text = (fb_event['info']['name'] + ' ' + fb_event['info'].get('description', '')).lower()
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
