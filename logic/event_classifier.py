# -*-*- encoding: utf-8 -*-*-

import codecs
import logging
import math
import re
from spitfire.runtime.filters import skip_filter

# TODO: translate to english before we try to apply the keyword matches
# TODO: if event creator has created dance events previously, give it some weight
# TODO: 

# TODO: for each style-keyword, give it some weight. don't be a requirement but yet-another-bayes-input
# TODO: add a bunch of classifier logic
# TODO: for iffy events, assume @ in the title means its a club event. same with monday(s) tuesday(s) etc.
# TODO: house class, house workshop, etc, etc. since 'house' by itself isn't sufficient
# maybe feed keywords into auto-classifying event type? bleh.

easy_dance_keywords = [
    'dances?', 'dancing', 'dancers?',
    u'ダンサー', # japanese dance
    u'舞', # chinese dance
    u'舞蹈', # chinese dance
    u'舞蹈的', # chinese dance
    'danse', 'danser', 'danseurs?', # french
    'tancerzy', # dancer polish
    'tanecznej', # dance polish
    'tancerka', # dance polish
    'tanecznych', #dance polish
    u'tańca', # dance polish
    'taneczne', # dance polish
    'tancerzami', #dancers polish
    u'dança', # dancing portuguese
    u'dançar', # dance portuguese
    'danzatore', # dancer italian
    u'bailarína?', # dancer spanish
    'danzas', # dance spanish
    'baile', # dance spanish
    u'šoku', # dance lithuanian
    u'šokti', # dance (verb) lithuanian
    u'šokis', # dance lithuanian
    u'šokyje', # dance lithuanian
    u'šokėjų', # dance (noun) lithuanian
    u'šokėju', # dancer lithuanian
    'ballerino', # dancer italian
    u'tänzern', # dancer german
    'footwork',
]
easy_choreography_keywords = [
    'choreograph(?:y|ed)', 'choreographers?', 'choreo',
    'coreografie', # italian
    'koreografi', # swedish
    'choreografien', # german
    'choreografams' # choreographer lithuanian
    'choreografijas', # choreography lithuanian
    u'choreografów', # choreographer polish
    'coreografiche', # choreographic italian
]

dance_and_music_keywords = [
    'hip\W?hop',
    'hip\W?hopo', # lithuanian hiphop
    'hip\W?hopu', # polish hiphop
    'funk',
    'dance\W?hall',
    'ragga',
    'hype',
    'new\W?jack\W?swing',
    'breaks',
    'boogaloo',
    'breaking?', 'breakers?',
    'free\W?style',
    'jerk',
    'kpop',
    'rnb',
    'hard\Whitting',
    'old\W?school hip\W?hop',
    '90\W?s hip\W?hop',
]

# hiphop dance. hiphop dans?
dance_keywords = [
    'breakingu', #breaking polish
    'swag',
    'jazz rock',
    'poppers?', 'popp?i?ng?',
    'poppeurs?',
    'commercial hip\W?hop',
    'jerk(?:ers?|ing?)',
    'street\W?dancing?',
    'street\W?dance', 'bre?ak\W?dance', 'bre?ak\W?dancing?', 'brea?ak\W?dancers?',
    'turfing?', 'turf danc\w+', 'flexing?', 'bucking?', 'jooking?',
    'b\W?boy[sz]?', 'b\W?boying?', 'b\W?girl[sz]?', 'b\W?girling?', 'power\W?moves?', 'footworking?',
    'breakeuse', # french bgirl
    'footworks', # spanish footworks
    'top\W?rock(?:s|er[sz]?|ing?)?', 'up\W?rock(?:s|er[sz]?|ing?|)?',
    'houser[sz]?', 'house ?danc\w*',
    'dance house', # seen in italian
    'lock(?:er[sz]?|ing?)?', 'lock dance',
    '[uw]h?aa?c?c?ker[sz]?', '[uw]h?aa?cc?kinn?g?', '[uw]h?aa?cc?k', # waacking
    'paa?nc?king?', # punking
    'locking4life',
    'dance crew[sz]?',
    'waving?', 'wavers?',
    'bott?ing?',
    'robott?ing?',
    'shuffle', 'melbourne shuffle',
    'jump\W?style[sz]?',
    'strutter[sz]?', 'strutting',
    'glides?', 'gliding', 
    'tuts?', 'tutting?', 'tutter[sz]?',
    'mtv\W?style', 'mtv\W?dance', 'videoclip', 'videodance', 'l\W?a\W?\Wstyle',
    'dance style[sz]',
    'n(?:ew|u)\W?styles?', 'all\W?style[zs]?', 'mix(?:ed)?\W?style[sz]?', 'open\W?style[sz]',
    'tout\W?style[zs]?', # french all-styles
    'me against the music',
    'krump', 'krumping?', 'krumper[sz]?',
    'girl\W?s\W?hip\W?hop',
    'hip\W?hopp?er[sz]?',
    'street\W?jazz', 'street\W?funk', 'jazz\W?funk', 'boom\W?crack',
    'hype danc\w*',
    'social hip\W?hop', 'hip\W?hop social dance[sz]',
    '(?:new|nu|middle)\W?s(?:ch|k)ool hip\W?hop', 'hip\W?hop (?:old|new|nu|middle)\W?s(?:ch|k)ool',
    'newstyleurs?',
    'vogue', 'voguer[sz]?', 'vogue?ing', 'vogue fem', 'voguin',
    'mini\W?ball', 'realness',
    'urban danc\w*',
    'danzas urbanas', # spanish urban dance
    'baile urbano', # spanish urban dance
    'pop\W{0,3}lock(?:ing?|er[sz]?)?'
]

easy_event_keywords = [
    'jams?', 'club', 'after\Wparty', 'pre\Wparty',
    'open sessions?', 'training',
]
club_and_event_keywords = [
    'sesja', # polish session
    u'セッション', # japanese sessions
    'sessions', 'practice',
    'shows?', 'performances?', 'contests?',
    'dancecontests', # dance contests german
    'esibizioni', #italian performance/exhibition
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
    'techno', 'trance', 'indie', 'glitch',
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
    'gogo',
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
    'poppin.? bottles?',
    'dance fitness',
    'lock down',
]
# battle royale
# go\W?go\W?danc(?:ers?|ing?)
#in\Whouse  ??
# 'brad houser'
# world class
# 1st class

# open mic
# Marvellous dance crew (uuugh)

#dj.*bboy
#dj.*bgirl

# 'vote for xx' in the subject
# 'vote on' 'vote for' in body, but small body of text
# release party

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
    'street\W?jam',
    'crew battle[sz]?', 'exhibition battle[sz]?',
    'apache line',
    'battle of the year', 'boty', 'compete', 'competitions?',
    'konkursams', # lithuanian competition
    u'čempionatams', # lithuanian championship
    'battles?',
    u'バトル', # japanese battle
    'batallas', # battles spanish
    'zawody', # polish battle/contest
    'walki', # polish battle/fight
    u'walkę', # polish battle/fight
    'bitwa', # polish battle
    'bitwach', # polish battle
    'tournaments?',
    'turniejach', # tournament polish
    'preselections?',
    u'présélections?', # preselections french
    'jurys?', 'jurados', 'judge[sz]?',
    'jueces', # spanish judges
    'giuria', # jury italian
    'showcase',
    r'(?:seven|7)\W*(?:to|two|2)\W*smoke',
    'c(?:y|i)ph(?:a|ers?)',
    u'サイファ', # japanese cypher
    u'サイファー', # japanese cypher
    'session', # the plural 'sessions' is handled up above under club-and-event keywords
    'workshops?',
    #'stage', # italian workshop, too noisy until we have per-language keywords
    'warsztaty', # polish workshop
    u'warsztatów', # polish workshop
    u'seminarų', # lithuanian workshop
    'class with', 'master\W?class(?:es)?',
    'auditions?',
    'audizione', # italian audition
    'naborem', # polish recruitment/audition
    'try\W?outs?', 'class(?:es)?', 'lessons?', 'courses?',
    'aulas?', # portuguese class(?:es)?
    'dansklasser', # swedish dance classes
    'lekcja', # polish lesson
    'eigoje', # lithuanian course
    'pamokas', # lithuanian lesson
    'kursai', # course lithuanian
    'lezione', # lession italian
    u'zajęciach', # class polish
    u'zajęcia', # classes polish
    'classi',
    'cours', 'clases?',
    'corso',  # lesson italian
    'abdc', 'america\W?s best dance crew',
    'crew\W?v[sz]?\W?crew',
    'prelims?',
    'bonnie\s*(?:and|&)\s*clyde',
] + [u'%s[ -]?(?:v/s|vs?\\.?|x|×|on)[ -]?%s' % (i, i) for i in range(12)]
event_keywords += [r'%s[ -]?na[ -]?%s' % (i, i) for i in range(12)] # polish x vs x


dance_wrong_style_keywords = [
    'styling', 'salsa', 'bachata', 'balboa', 'tango', 'latin', 'lindy', 'lindyhop', 'swing', 'wcs', 'samba',
    'barre',
    'musical theat(?:re|er)',
    'pole dance', 'flirt dance',
    'bollywood', 'kalbeliya', 'bhawai', 'teratali', 'ghumar',
    'oriental', 'oriente', 'orientale',
    'tahitian dancing',
    'folkloric',
    'kizomba',
    'burlesque',
    'technique', 'limon',
    'clogging',
    'zouk',
    # Sometimes used in studio name even though it's still a hiphop class:
    #'ballroom',
    #'ballet',
    'jazz', 'tap', 'contemporary',
    'african',
    'zumba', 'belly\W?danc(?:e(?:rs?)?|ing)', 'bellycraft', 'worldbellydancealliance',
    'soca',
    'flamenco',
]

all_regexes = {}

def build_regexes():
    if all_regexes['good_capturing_keyword_regex']:
        return

    manual_dance_keywords = []
    import os
    if os.getcwd().endswith('mapreduce'): #TODO(lambert): what is going on with appengine sticking me in the wrong starting directory??
        base_dir = '..'
    else:
        base_dir = '.'
    for filename in ['bboy_crews', 'bboys', 'choreo_crews', 'choreo_dancers', 'choreo_keywords', 'competitions', 'freestyle_crews', 'freestyle_dancers', 'freestyle_keywords']:
        f = codecs.open('%s/dance_keywords/%s.txt' % (base_dir, filename), encoding='utf-8')
        for line in f.readlines():
            line = re.sub('\s*#.*', '', line.strip())
            if not line:
                continue
            if line.endswith(',0'):
                line = line[:-2]
            else:
                manual_dance_keywords.append(line)

    if manual_dance_keywords:
        all_regexes['manual_dance_keywords_regex'] = make_regex(manual_dance_keywords)
    else:
        all_regexes['manual_dance_keywords_regex'] = re.compile(r'NEVER_MATCH_BLAGSDFSDFSEF')

    all_regexes['good_capturing_keyword_regex'] = make_regex(easy_dance_keywords + easy_event_keywords + dance_keywords + event_keywords + club_and_event_keywords + dance_and_music_keywords + easy_choreography_keywords + manual_dance_keywords, matching=True)

def make_regex(strings, matching=False, word_boundaries=True):
    u = u'|'.join(strings)
    if matching:
        regex = u'(?ui)(' + u + u')'
    else:
        regex = u'(?ui)(?:' + u + u')'
    if word_boundaries:
        regex = r'\b%s\b' % regex
    return re.compile(regex)

all_regexes['dance_wrong_style_regex'] = make_regex(dance_wrong_style_keywords)
all_regexes['dance_and_music_regex'] = make_regex(dance_and_music_keywords)
all_regexes['club_and_event_regex'] = make_regex(club_and_event_keywords)
all_regexes['easy_choreography_regex'] = make_regex(easy_choreography_keywords)
all_regexes['club_only_regex'] = make_regex(club_only_keywords)

all_regexes['easy_dance_regex'] = make_regex(easy_dance_keywords)
all_regexes['easy_event_regex'] = make_regex(easy_event_keywords)
all_regexes['dance_regex'] = make_regex(dance_keywords)
all_regexes['event_regex'] = make_regex(event_keywords)

all_regexes['bad_capturing_keyword_regex'] = make_regex(club_only_keywords + dance_wrong_style_keywords, matching=True)


# NOTE: Eventually we can extend this with more intelligent heuristics, trained models, etc, based on multiple keyword weights, names of teachers and crews and whatnot

def get_relevant_text(fb_event):
    search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
    return search_text

class ClassifiedEvent(object):
    def __init__(self, fb_event, language):
        if 'name' not in fb_event['info']:
            logging.info("fb event id is %s has no name, with value %s", fb_event['info']['id'], fb_event)
            self.search_text = ''
        else:
            self.search_text = get_relevant_text(fb_event)
        self.language = language

    def classify(self):
        build_regexes()
        manual_dance_keywords_matches = all_regexes['manual_dance_keywords_regex'].findall(self.search_text)
        easy_dance_matches = all_regexes['easy_dance_regex'].findall(self.search_text)
        easy_event_matches = all_regexes['easy_event_regex'].findall(self.search_text)
        dance_matches = all_regexes['dance_regex'].findall(self.search_text)
        event_matches = all_regexes['event_regex'].findall(self.search_text)
        dance_wrong_style_matches = all_regexes['dance_wrong_style_regex'].findall(self.search_text)
        dance_and_music_matches = all_regexes['dance_and_music_regex'].findall(self.search_text)
        club_and_event_matches = all_regexes['club_and_event_regex'].findall(self.search_text)
        easy_choreography_matches = all_regexes['easy_choreography_regex'].findall(self.search_text)
        club_only_matches = all_regexes['club_only_regex'].findall(self.search_text)

        self.found_dance_matches = dance_matches + easy_dance_matches + dance_and_music_matches + manual_dance_keywords_matches + easy_choreography_matches
        self.found_event_matches = event_matches + easy_event_matches + club_and_event_matches
        self.found_wrong_matches = dance_wrong_style_matches + club_only_matches

        if len(manual_dance_keywords_matches) >= 1:
            self.dance_event = 'obvious dancer or dance crew or battle'
        # one critical dance keyword
        elif len(dance_matches) >= 1:
            self.dance_event = 'obvious dance style'
        elif len(dance_and_music_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1:
            self.dance_event = 'hiphop/funk and good event type'
        # one critical event and a basic dance keyword and not a wrong-dance-style and not a generic-club
        elif len(easy_dance_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1 and len(dance_wrong_style_matches) == 0:
            self.dance_event = 'dance event thats not a bad-style'
        elif len(easy_dance_matches) >= 1 and len(club_and_event_matches) >= 1 and len(dance_wrong_style_matches) == 0 and len(club_only_matches) == 0:
            self.dance_event = 'dance show thats not a club'
        else:
            self.dance_event = False

    def is_dance_event(self):
        return bool(self.dance_event)
    def reason(self):
        return self.dance_event
    def dance_matches(self):
        return set(self.found_dance_matches)
    def event_matches(self):
        return set(self.found_event_matches)
    def wrong_matches(self):
        return set(self.found_wrong_matches)
    def match_score(self):
        if self.is_dance_event():
            combined_matches = self.found_dance_matches + self.found_event_matches
            return len(combined_matches)
        else:
            return 0
    def keyword_density(self):
        combined_matches = self.found_dance_matches + self.found_event_matches
        fraction_matched = 1.0 * len(combined_matches) / len(re.split(r'\W+', self.search_text))
        if not fraction_matched:
            return -100
        else:
            return int(math.log(fraction_matched, 2))


def get_classified_event(fb_event, language):
    classified_event = ClassifiedEvent(fb_event, language)
    classified_event.classify()
    return classified_event

def relevant_keywords(fb_event):
    build_regexes()
    text = get_relevant_text(fb_event)
    good_keywords = all_regexes['good_capturing_keyword_regex'].findall(text)
    bad_keywords = all_regexes['bad_capturing_keyword_regex'].findall(text)
    return sorted(set(good_keywords).union(bad_keywords))

@skip_filter
def highlight_keywords(text):
    build_regexes()
    text = all_regexes['good_capturing_keyword_regex'].sub('<span class="matched-text">\\1</span>', text)
    text = all_regexes['bad_capturing_keyword_regex'].sub('<span class="bad-matched-text">\\1</span>', text)
    return text

