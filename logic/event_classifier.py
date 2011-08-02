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
    'dances?', 'dancing', 'dancers?', 'danser',
    'hitting', 'footwork',
]
easy_choreography_keywords = [
    'choreograph(?:y|ed)', 'choreographers?',
]

dance_and_music_keywords = [
    'hip.?hop',
    'funk',
    'dance.?hall',
    'ragga',
    'hype',
    'new jack swing',
    'breaks',
    'boogaloo',
    'breaking?', 'breakers?',
    'free.?style',
    'jerk',
]

dance_keywords = [
    'poppers?', 'popp?i?ng?',

    'jerk(?:ers?|ing?)',
    'street.?dancing?',
    'street.?dance', 'break.?dance', 'break.?dancing?',
    'turfing?', 'turf danc\w+', 'flexing?', 'bucking?', 'jooking?',
    'b.?boy[sz]?', 'b.?boying?', 'b.?girl[sz]?', 'b.?girling?', 'power.?moves?', 'footworking?',
    'top.?rock(?:er[sz]?|ing?)?', 'up.?rock(?:er[sz]?|ing?|)?',
    'houser[sz]?', 'house ?danc\w*',
    'lock(?:er[sz]?|ing?)?', 'lock dance',
    'wh?aa?cc?ker[sz]?', 'wh?aa?cc?king?', 'wh?aa?cc?k',
    'locking4life',
    'waving?', 'wavers?',
    'robott?ing?',
    'shuffle', 'melbourne shuffle',
    'strutter[sz]?', 'strutting',
    'glides?', 'gliding', 
    'tuts?', 'tutting?', 'tutter[sz]?',
    'mtv.?style',
    'dance style[sz]',
    'n(?:ew|u).?styles?', 'all.?style[zs]?', 'mix(?:ed)?.?style[sz]?'
    'me against the music',
    'krump', 'krumping?', 'krumper[sz]?',
    'girl.s.?hip.?hop',
    'hip.?hopp?er[sz]?',
    'choreo', 'street jazz', 'street funk', 'jazz funk', 'boom crack',
    'hype danc\w*', '90.?s hip.?hop', 'social hip.?hop', 'old school hip.?hop',
    'vogue', 'voguer[sz]?', 'vogue?ing',
    'urban danc\w*',
    'pop\W{0,3}lock(?:ing?|er[sz]?)'
]

easy_event_keywords = [
    'jams?', 'club', 'after.party', 'pre.party',
]
club_and_event_keywords = [
    'sessions',
    'shows?', 'performances?', 'contests?',
]

club_only_keywords = [
    'club',
    'bottle service',
    'table service',
    'coat check',
    #'rsvp',
    'free before',
    #'dance floor',
    #'bar',
    #'live',
    #'and up',
    'vip',
    'guest.?list',
    'drink specials?',
    'resident dj.?s?',
    'dj.?s?',
    'electro', 'techno', 'trance', 'indie', 'glitch', 'dubstep',
    'bands?',
    'dress to',
    'mixtape',
    'decks',
    'r&b',
    'local dj.?s?',
    'all night',
    'lounge',
    'live performances?',
    'doors', # doors open at x
    'restaurant',
    'hotel',
    'music shows?',
    'a night of',
    'dance floor',
    'beer',
    'blues',
    'bartenders?',
    'waiters?',
    'waitress(?:es)?',
    'go\Wgo',
]

#TODO(lambert): use these
anti_dance_keywords  = [
    'jerk chicken',
    'poker tournaments?',
    'fashion competition',
    'wrestling competition',
    't?shirt competition',
    'shaking competition',
    'costume competition',
    'bottles? popping?',
    'dance fitness',
]
# battle royale
# go.?go.?danc(?:ers?|ing?)
#in.house  ??
# 'brad houser'
# world class
# 1st class

#dj.*bboy
#dj.*bgirl

# 'vote for xx' in the subject
# 'vote on' 'vote for' in body, but small body of text

# methodology
# cardio
# fitness

# sometimes dance performances have Credits with a bunch of other performers, texts, production, etc. maybe remove these?

# HIP HOP INTERNATIONAL

# bad words in title of club events
# DJ
# Live
# Mon/Tue/Wed/Thu/Fri/Sat
# Guests?

#TODO(lambert): use these to filter out shows we don't really care about
other_show_keywords = [
    'comedy',
    'poetry',
    'poets?',
    'spoken word',
    'painting',
    'juggling',
    'magic',
    'singing',
    'acting',
]

event_keywords = [
    'crew battle[sz]?', 'exhibition battle[sz]?',
    'boty', 'competitions?', 'battles?', 'tournaments?', 'judge[sz]?', 'jury', 'preselection',
    r'(?:seven|7)\W*(?:to|two|2)\W*smoke',
    'c(?:y|i)phers?',
    'session', # the plural 'sessions' is handled up above under club-and-event keywords
    'workshops?', 'class with', 'master\W?class(?:es)?', 'auditions?', 'try.?outs?', 'class(?:es)?',
    'cours',
    'abdc', 'america.?s best dance crew',
] + [r'%s[ -]?(?:vs?\.?|x|×|on)[ -]?%s' % (i, i) for i in range(12)]


dance_wrong_style_keywords = [
    'styling', 'salsa', 'tango', 'latin', 'lindy', 'swing', 'wcs', 'samba',
    'technique',
    # Sometimes used in studio name even though it's still a hiphop class:
    #'ballroom',
    #'ballet',
    'jazz', 'tap', 'contemporary',
    'african',
    'zumba', 'belly.?danc(?:e(?:rs?)?|ing)',
    'soca',
    'flamenco',
]

dance_wrong_style_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(dance_wrong_style_keywords))
dance_and_music_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(dance_and_music_keywords))
club_and_event_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(club_and_event_keywords))
easy_choreography_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(easy_choreography_keywords))
club_only_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(club_only_keywords))

easy_dance_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(easy_dance_keywords))
easy_event_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(easy_event_keywords))
dance_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(dance_keywords))
event_regex = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(event_keywords))

good_capturing_keyword_regex = re.compile(r'(?i)\b(%s)\b' % '|'.join(easy_dance_keywords + easy_event_keywords + dance_keywords + event_keywords + club_and_event_keywords + dance_and_music_keywords + easy_choreography_keywords))
bad_capturing_keyword_regex = re.compile(r'(?i)\b(%s)\b' % '|'.join(club_only_keywords + dance_wrong_style_keywords))


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
    dance_wrong_style_matches = set(dance_wrong_style_regex.findall(search_text))
    dance_and_music_matches = set(dance_and_music_regex.findall(search_text))
    club_and_event_matches = set(club_and_event_regex.findall(search_text))
    easy_choreography_matches = set(easy_choreography_regex.findall(search_text))
    club_only_matches = set(club_only_regex.findall(search_text))

    # one critical dance keyword
    if len(dance_matches) >= 1:
        return True, 'obvious dance style', dance_matches.union(easy_dance_matches).union(dance_and_music_matches), event_matches.union(easy_event_matches)
    # if we have hiphop/funk, then ensure we have a strong event-keyword match
    #elif len(dance_and_music_matches) >= 1 and len(easy_event_matches) >= 1 and len(club_only_matches) == 0:
    #    return True, 'hiphop/funk and not club', dance_matches.union(easy_dance_matches).union(dance_and_music_matches).union(easy_choreography_matches), event_matches.union(easy_event_matches)
    elif len(dance_and_music_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1:
        return True, 'hiphop/funk and good event type', dance_matches.union(easy_dance_matches).union(dance_and_music_matches).union(easy_choreography_matches), event_matches.union(easy_event_matches)
     # one critical event and a basic dance keyword and not a wrong-dance-style and not a generic-club
    elif len(easy_dance_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1 and len(dance_wrong_style_matches) == 0:
        return True, 'dance event thats not a bad-style', dance_matches.union(easy_dance_matches).union(dance_and_music_matches), event_matches.union(easy_event_matches)
    elif len(easy_dance_matches) >= 1 and len(club_and_event_matches) >= 1 and len(dance_wrong_style_matches) == 0 and len(club_only_matches) == 0:
        return True, 'dance show thats not a club', dance_matches.union(easy_dance_matches).union(dance_and_music_matches), event_matches.union(easy_event_matches).union(club_and_event_matches)
    else:
        return False#, 'nothing', dance_wrong_style_matches, club_only_matches

@skip_filter
def highlight_keywords(text):
    text = good_capturing_keyword_regex.sub('<span class="matched-text">\\1</span>', text)
    text = bad_capturing_keyword_regex.sub('<span class="bad-matched-text">\\1</span>', text)
    return text
