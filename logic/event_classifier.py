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
    'choreograph(?:y|ed)', 'choreographers?', 'choreo',

]

dance_and_music_keywords = [
    'hip\W?hop',
    'funk',
    'dance.?hall',
    'ragga',
    'hype',
    'new\W?jack\W?swing',
    'breaks',
    'boogaloo',
    'breaking?', 'breakers?',
    'free\W?style',
    'jerk',
    'kpop',
]

# hiphop dance. hiphop dans?
dance_keywords = [
    'poppers?', 'popp?i?ng?',

    'commercial hip\W?hop',
    'jerk(?:ers?|ing?)',
    'street\W?dancing?',
    'street\W?dance', 'break\W?dance', 'break\W?dancing?',
    'turfing?', 'turf danc\w+', 'flexing?', 'bucking?', 'jooking?',
    'b\W?boy[sz]?', 'b\W?boying?', 'b\W?girl[sz]?', 'b\W?girling?', 'power\W?moves?', 'footworking?',
    'top\W?rock(?:er[sz]?|ing?)?', 'up\W?rock(?:er[sz]?|ing?|)?',
    'houser[sz]?', 'house ?danc\w*',
    'lock(?:er[sz]?|ing?)?', 'lock dance',
    'wh?aa?c?c?ker[sz]?', 'wh?a?a?cc?king?', 'wh?a?a?cc?k',
    'locking4life',
    'dance crew[sz]?',
    'waving?', 'wavers?',
    'bott?ing?',
    'robott?ing?',
    'shuffle', 'melbourne shuffle',
    'strutter[sz]?', 'strutting',
    'glides?', 'gliding', 
    'tuts?', 'tutting?', 'tutter[sz]?',
    'mtv\W?style',
    'mtv\W?dance',
    'dance style[sz]',
    'n(?:ew|u)\W?styles?', 'all\W?style[zs]?', 'mix(?:ed)?\W?style[sz]?'
    'me against the music',
    'krump', 'krumping?', 'krumper[sz]?',
    'girl\W?s\W?hip\W?hop',
    'hip\W?hopp?er[sz]?',
    'street\W?jazz', 'street\W?funk', 'jazz\W?funk', 'boom\W?crack',
    'hype danc\w*', '90\W?s hip\W?hop', 'social hip\W?hop', 'old school hip\W?hop',
    'vogue', 'voguer[sz]?', 'vogue?ing',
    'urban danc\w*',
    'pop\W{0,3}lock(?:ing?|er[sz]?)?'
]

easy_event_keywords = [
    'jams?', 'club', 'after\Wparty', 'pre\Wparty',
    'open sessions?', 'training',
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
    'guest\W?list',
    'drink specials?',
    'resident dj\W?s?',
    'dj\W?s?',
    'electro', 'techno', 'trance', 'indie', 'glitch', 'dubstep',
    'bands?',
    'dress to',
    'mixtape',
    'decks',
    'r&b',
    'local dj\W?s?',
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
    'popping? bottles?',
    'dance fitness',
    'lock down',
]
# battle royale
# go\W?go\W?danc(?:ers?|ing?)
#in\Whouse  ??
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
# 21+ 18+

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
    'apache line',
    'battle of the year', 'boty', 'competitions?', 'battles?', 'tournaments?', 'judge[sz]?', 'jury', 'preselection',
    'showcase',
    r'(?:seven|7)\W*(?:to|two|2)\W*smoke',
    'c(?:y|i)ph(?:a|ers?)',
    'session', # the plural 'sessions' is handled up above under club-and-event keywords
    'workshops?', 'class with', 'master\W?class(?:es)?', 'auditions?', 'try\W?outs?', 'class(?:es)?', 'lessons?',
    'cours',
    'abdc', 'america\W?s best dance crew',
    'crew\W?v[sz]?\W?crew',
    'prelims?',
    'bonnie\s*(?:and|&)\s*clyde',
] + [r'%s[ -]?(?:vs?\.?|x|×|on)[ -]?%s' % (i, i) for i in range(12)]


dance_wrong_style_keywords = [
    'styling', 'salsa', 'balboa', 'tango', 'latin', 'lindy', 'swing', 'wcs', 'samba',
    'burlesque',
    'technique',
    # Sometimes used in studio name even though it's still a hiphop class:
    #'ballroom',
    #'ballet',
    'jazz', 'tap', 'contemporary',
    'african',
    'zumba', 'belly\W?danc(?:e(?:rs?)?|ing)',
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

def get_relevant_text(fb_event):
    search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
    return search_text

def is_dance_event(fb_event):
    if 'name' not in fb_event['info']:
        logging.info("fb event id is %s has no name, with value %s", fb_event['info']['id'], fb_event)
        return False
    search_text = get_relevant_text(fb_event)
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
        return (
            True,
            'obvious dance style',
            dance_matches.union(easy_dance_matches).union(dance_and_music_matches),
            event_matches.union(easy_event_matches)
        )
    # if we have hiphop/funk, then ensure we have a strong event-keyword match
    #elif len(dance_and_music_matches) >= 1 and len(easy_event_matches) >= 1 and len(club_only_matches) == 0:
    #    return True, 'hiphop/funk and not club', dance_matches.union(easy_dance_matches).union(dance_and_music_matches).union(easy_choreography_matches), event_matches.union(easy_event_matches)
    elif len(dance_and_music_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1:
        return (
            True,
            'hiphop/funk and good event type',
            dance_matches.union(easy_dance_matches).union(dance_and_music_matches).union(easy_choreography_matches),
            event_matches.union(easy_event_matches)
        )
     # one critical event and a basic dance keyword and not a wrong-dance-style and not a generic-club
    elif len(easy_dance_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1 and len(dance_wrong_style_matches) == 0:
        return (
            True,
            'dance event thats not a bad-style',
            dance_matches.union(easy_dance_matches).union(dance_and_music_matches).union(easy_choreography_matches),
            event_matches.union(easy_event_matches)
        )
    elif len(easy_dance_matches) >= 1 and len(club_and_event_matches) >= 1 and len(dance_wrong_style_matches) == 0 and len(club_only_matches) == 0:
        return (
            True,
            'dance show thats not a club',
            dance_matches.union(easy_dance_matches).union(dance_and_music_matches),
            event_matches.union(easy_event_matches).union(club_and_event_matches)
        )
    else:
        return False#, 'nothing', dance_wrong_style_matches, club_only_matches

def relevant_keywords(fb_event):
    text = get_relevant_text(fb_event)
    good_keywords = good_capturing_keyword_regex.findall(text)
    bad_keywords = bad_capturing_keyword_regex.findall(text)
    return sorted(set(good_keywords).union(bad_keywords))

@skip_filter
def highlight_keywords(text):
    text = good_capturing_keyword_regex.sub('<span class="matched-text">\\1</span>', text)
    text = bad_capturing_keyword_regex.sub('<span class="bad-matched-text">\\1</span>', text)
    return text
