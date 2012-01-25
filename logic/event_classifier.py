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
    'dance style[sz]',
    'dances?', 'dancing', 'dancers?',
    u'ダンサー', # japanese dance
    u'ダンス', # japanese dance
    u'舞者', # chinese dancer
    u'舞技', # chinese dancing
    u'舞', # chinese dance
    u'舞蹈', # chinese dance
    u'舞蹈的', # chinese dance
    u'排舞', # chinese dance
    u'เต้น', # dance thai
    'danse\w*', # french
    'taniec', # dance polish
    'tan[ec][ec]\w*', # dance polish
    u'tancujú', # dance slovak
    u'tanečno', # dance slovak
    u'danç\w*', # dance portuguese
    u'tańc\w*', # dance polish
    u'taneč\w*', # dance czech
    'tancovat', # dance czech
    'danza\w*', # dance italian
    u'šok\w*', # dance lithuanian
    'tanz\w*', # dance german
    'tanssi\w*' # finnish dance
    'bail[ae]\w*', # dance spanish
    'danzas', # dance spanish
    'ballerino', # dancer italian
    u'tänzern', # dancer german
    u'танчер', # dancer macedonian
    u'танцовиот', # dance macedonian
    'footwork',
    'plesa', # dance croatian
    'plesu', # dancing croatian
    u'nhảy', # dance vietnamese
    u'tänzer', # dancer german
]
easy_choreography_keywords = [
    '(?:ch|k|c)oreogra(?:ph|f)\w*', #english, italian, finnish, swedish, german, lithuanian, polish, italian, spanish, portuguese
    'choreo',
    u'chorée', # french choreo
    u'chorégraphe', # french choreographer
    u'кореограф', # macedonian
]

dance_and_music_keywords = [
    'hip\W?hop',
    u'хипхоп', # macedonian hiphop
    u'ヒップホップ', # hiphop japanese
    'hip\W?hop\w*', # lithuanian, polish hiphop
    'all\W?style[zs]?',
    'tout\W?style[zs]?', # french all-styles
    'tutti gli stili', # italian all-styles
    'swag',
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
    'freestylers?',
    'breakingu', #breaking polish
    u'breaktánc', # breakdance hungarian
    'jazz rock',
    'poppers?', 'popp?i?ng?',
    'poppeurs?',
    'commercial hip\W?hop',
    'jerk(?:ers?|ing?)',
    'street\W?dancing?',
    u'gatvės šokių', # lithuanian streetdance
    'katutanssi\w*', # finnish streetdance
    'street\W?dance', 'bre?ak\W?dance', 'bre?ak\W?dancing?', 'brea?ak\W?dancers?',
    'turfing?', 'turf danc\w+', 'flexing?', 'bucking?', 'jooking?',
    'b\W?boy[sz]?', 'b\W?boying?', 'b\W?girl[sz]?', 'b\W?girling?', 'power\W?moves?', 'footworking?',
    u'파워무브', # powermove korean
    'breakeuse', # french bgirl
    'footworks', # spanish footworks
    'top\W?rock(?:s|er[sz]?|ing?)?', 'up\W?rock(?:s|er[sz]?|ing?|)?',
    'houser[sz]?', 'house ?danc\w*',
    'dance house', # seen in italian
    'lock(?:er[sz]?|ing?)?', 'lock dance',
    u'ロッカーズ', # japanese lockers
    u'ロッカ', # japanese lock
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
    'n(?:ew|u)\W?styles?',
    'mix(?:ed)?\W?style[sz]?', 'open\W?style[sz]',
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
    u'danças urbanas', # portuguese urban dance
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
    u'セッション', # session japanese
    'shows?', 'performances?', 'contests?',
    u'秀', # chinese show
    u'的表演', # chinese performance
    u'表演', # chinese performance
    u'パフォーマンス', # japanese performance
    'konkurrencer', # danish contest
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
# lock up
# battle freestyle ?
# dj battle
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

# boogiezone if not contemporary?
# free style if not salsa?

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
    u'thi nhảy', # dance competition vietnam
    'kilpailu\w*' # finish competition
    'konkursams', # lithuanian competition
    'verseny', # hungarian competition
    u'čempionatams', # lithuanian championship
    'campeonato', # spanish championship
    'meisterschaft', # german championship
    'battles?',
    u'バトル', # japanese battle
    'batallas', # battles spanish
    'zawody', # polish battle/contest
    'walki', # polish battle/fight
    u'walkę', # polish battle/fight
    'bitwa', # polish battle
    'bitwach', # polish battle
    u'バトル', # japanese battle
    'tournaments?',
    u'大会', # japanese tournament
    u'トーナメント', # japanese tournament
    'turnie\w*', # tournament polish/german
    u'giải đấu', # tournament vietnamese
    'turneringer', # danish tournament
    'preselections?',
    u'présélections?', # preselections french
    'jurys?',
    'jurados?', # spanish jury
    'judge[sz]?',
    u'teisėjai', # lithuanian judges
    'tuomaristo', # jury finnish
    'jueces', # spanish judges
    'giuria', # jury italian
    'showcase',
    r'(?:seven|7)\W*(?:to|two|2)\W*smoke',
    'c(?:y|i)ph(?:a|ers?)',
    u'サイファ', # japanese cypher
    u'サイファー', # japanese cypher
    'session', # the plural 'sessions' is handled up above under club-and-event keywords
    'workshops?',
    'talleres', # workshops spanish
    'radionicama', # workshop croatian
    #'stage', # italian workshop, too noisy until we have per-language keywords
    'warsztaty', # polish workshop
    u'warsztatów', # polish workshop
    u'seminarų', # lithuanian workshop
    'class with', 'master\W?class(?:es)?',
    'auditions?',
    'audiciones', # spanish audition
    u'試鏡', # chinese audition
    'audizione', # italian audition
    'naborem', # polish recruitment/audition
    'try\W?outs?', 'class(?:es)?', 'lessons?', 'courses?',
    u'수업', # korean class
    u'수업을', # korean classes
    'lekci', # czech lesson
    u'課程', # course chinese
    u'課', # class chinese
    u'堂課', # lesson chinese
    'concorso', # course italian
    'kurs(?:y|en)?', # course german/polish
    'aulas?', # portuguese class(?:es)?
    u'특강', # korean lecture
    'lekcie', # slovak lessons
    'dansklasser', # swedish dance classes
    'lekcja', # polish lesson
    'eigoje', # lithuanian course
    'pamokas', # lithuanian lesson
    'kursai', # course lithuanian
    'lezione', # lesson italian
    'lezioni', # lessons italian
    u'zajęciach', # class polish
    u'zajęcia', # classes polish
    u'คลาส', # class thai
    'classi',
    'cours', 'clases?',
    'corso',  # lesson italian
    'abdc', 'america\W?s best dance crew',
    'crew\W?v[sz]?\W?crew',
    'prelims?',
    u'初賽', # chinese preliminaries
    'bonnie\s*(?:and|&)\s*clyde',
] + [u'%s[ -]?(?:v/s|vs?\\.?|x|×|on)[ -]?%s' % (i, i) for i in range(12)]
event_keywords += [r'%s[ -]?na[ -]?%s' % (i, i) for i in range(12)] # polish x vs x


dance_wrong_style_keywords = [
    'styling', 'salsa', 'bachata', 'balboa', 'tango', 'latin', 'lindy', 'lindyhop', 'swing', 'wcs', 'samba',
    'tumbling',
    'exotic',
    'cheer',
    'barre',
    'contact improv',
    'contact improv\w*',
    'contratto mimo', # italian contact mime
    'musical theat(?:re|er)',
    'pole dance', 'flirt dance',
    'bollywood', 'kalbeliya', 'bhawai', 'teratali', 'ghumar',
    'oriental\w*', 'oriente', 
    'capoeira',
    'tahitian dancing',
    'folkloric',
    'kizomba',
    'burlesque',
    'technique', 'limon',
    'clogging',
    'zouk',
    'afro mundo',
    # Sometimes used in studio name even though it's still a hiphop class:
    #'ballroom',
    #'ballet',
    'jazz', 'tap', 'contemporary',
    'contemporanea', # contemporary italian
    'african',
    'zumba', 'belly\W?danc(?:e(?:rs?)?|ing)', 'bellycraft', 'worldbellydancealliance',
    'soca',
    'flamenco',
]

all_regexes = {}

def build_regexes():
    if 'good_capturing_keyword_regex' in all_regexes:
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
        all_regexes['manual_dance_keywords_regex'] = make_regexes(manual_dance_keywords)
    else:
        all_regexes['manual_dance_keywords_regex'] = re.compile(r'NEVER_MATCH_BLAGSDFSDFSEF')

    all_regexes['good_capturing_keyword_regex'] = make_regexes(easy_dance_keywords + easy_event_keywords + dance_keywords + event_keywords + club_and_event_keywords + dance_and_music_keywords + easy_choreography_keywords + manual_dance_keywords, matching=True)

def make_regex(strings, matching=False, word_boundaries=True):
    try:
        u = u'|'.join(strings)
        if matching:
            regex = u'(?ui)(' + u + u')'
        else:
            regex = u'(?ui)(?:' + u + u')'
        if word_boundaries:
            regex = r'\b%s\b' % regex
        return re.compile(regex)
    except UnicodeDecodeError:
        for line in strings:
            try:
                re.compile(u'|'.join([line]))
            except UnicodeDecodeError:
                logging.error("failed to compile: %r: %s", line, line)
        logging.fatal("Error constructing regexes")

WORD_BOUNDARIES = 0
NO_WORD_BOUNDARIES = 1
def make_regexes(strings, matching=False):
    a = [None] * 2
    a[NO_WORD_BOUNDARIES] = make_regex(strings, matching=matching, word_boundaries=False)
    a[WORD_BOUNDARIES] = make_regex(strings, matching=matching, word_boundaries=True)
    return tuple(a)

all_regexes['dance_wrong_style_regex'] = make_regexes(dance_wrong_style_keywords)
all_regexes['dance_and_music_regex'] = make_regexes(dance_and_music_keywords)
all_regexes['club_and_event_regex'] = make_regexes(club_and_event_keywords)
all_regexes['easy_choreography_regex'] = make_regexes(easy_choreography_keywords)
all_regexes['club_only_regex'] = make_regexes(club_only_keywords)

all_regexes['easy_dance_regex'] = make_regexes(easy_dance_keywords)
all_regexes['easy_event_regex'] = make_regexes(easy_event_keywords)
all_regexes['dance_regex'] = make_regexes(dance_keywords)
all_regexes['event_regex'] = make_regexes(event_keywords)

all_regexes['bad_capturing_keyword_regex'] = make_regexes(club_only_keywords + dance_wrong_style_keywords, matching=True)


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
        if self.language in ['ja', 'ko', 'zh-CN', 'zh-TW', 'th']:
            idx = NO_WORD_BOUNDARIES
        else:
            idx = WORD_BOUNDARIES
        manual_dance_keywords_matches = all_regexes['manual_dance_keywords_regex'][idx].findall(self.search_text)
        easy_dance_matches = all_regexes['easy_dance_regex'][idx].findall(self.search_text)
        easy_event_matches = all_regexes['easy_event_regex'][idx].findall(self.search_text)
        dance_matches = all_regexes['dance_regex'][idx].findall(self.search_text)
        event_matches = all_regexes['event_regex'][idx].findall(self.search_text)
        dance_wrong_style_matches = all_regexes['dance_wrong_style_regex'][idx].findall(self.search_text)
        dance_and_music_matches = all_regexes['dance_and_music_regex'][idx].findall(self.search_text)
        club_and_event_matches = all_regexes['club_and_event_regex'][idx].findall(self.search_text)
        easy_choreography_matches = all_regexes['easy_choreography_regex'][idx].findall(self.search_text)
        club_only_matches = all_regexes['club_only_regex'][idx].findall(self.search_text)

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
    #TODO(lambert): add language-support to this so we do better on foreign ones
    good_keywords = all_regexes['good_capturing_keyword_regex'][NO_WORD_BOUNDARIES].findall(text)
    bad_keywords = all_regexes['bad_capturing_keyword_regex'][NO_WORD_BOUNDARIES].findall(text)
    return sorted(set(good_keywords).union(bad_keywords))

@skip_filter
def highlight_keywords(text):
    build_regexes()
    #TODO(lambert): add language-support to this so we do better on foreign ones
    text = all_regexes['good_capturing_keyword_regex'][WORD_BOUNDARIES].sub('<span class="matched-text">\\1</span>', text)
    text = all_regexes['bad_capturing_keyword_regex'][WORD_BOUNDARIES].sub('<span class="bad-matched-text">\\1</span>', text)
    return text

