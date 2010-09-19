import re

dance_keywords = [
    'dances?', 'dancing', 'dancers?',
    'b.?boys?', 'b.?girls?', 'breaks', 'breaking', 'breakers?',
    'top.?rock(?:ers?|ing|)', 'up.?rock(?:ers?|ing|)',
    'housers?', 'house danc[^ ]*',
    'lockers?', 'locking',
    'poppers?', 'popping', 'hitting',
    'funk', 'g.?style',
    'animation', 'isolation', 'robots?',
    'strutters?', 'strutting',
    'glides?', 'gliding', 'waves?', 'waving', 'wavers?',
    'tuts?', 'tutting', 'tutters?',
    'hip.?hop',
    'choreography', 'choreographers?', 'choreo', 'street jazz', 'street funk', 'jazz funk',
    'new jack swing', 'hype danc[^ ]*', '90.?s hip.?hop', 'social hip.?hop', 'old schol hip.?hop',
    'w[ha]acking', 'w[ha]ackers?', 'w[ha]ack', 'punking', 'punkers?', 'punk',
    'vogue', 'voguers?', 'vogueing',
]

event_keywords = [
    'competitions?', 'battles?', 'tournaments?', 'jams?', 'contests?', 'judges?',
    'cyphers?', 'club',
    'sessions?', 'shows?', 'performances?',
    'workshops?', 'class with', 'master class(?:es)?', 'auditions?', 'try.?outs?', 'class(?:es)?',
    'abdc',
]

dance_regex = re.compile(r'\b(?:%s)\b' % '|'.join(dance_keywords))
event_regex = re.compile(r'\b(?:%s)\b' % '|'.join(event_keywords))

# NOTE: Eventually we can extend this with more intelligent heuristics, trained models, etc, based on multiple keyword weights, names of teachers and crews and whatnot

def is_dance_event(fb_event):
    search_text = (fb_event['info']['name'] + ' ' + fb_event['info'].get('description', '')).lower()
    dance_matches = dance_regex.findall(search_text)
    event_matches = event_regex.findall(search_text)
    return len(dance_matches) >= 1 and len(event_matches) >= 1
