# -*-*- encoding: utf-8 -*-*-

import codecs
import collections
import logging
import math
try:
    import re2
    import re2 as re
except ImportError:
    logging.info("Could not import re2, falling back to re.")
    re2 = None
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)
import time
from util import cjk_detect
from spitfire.runtime.filters import skip_filter
from logic import keywords
from logic import regex_keywords

USE_UNICODE = False

#TODO(lambert): eliminate these as part of refactoring
make_regex_string = regex_keywords.make_regex_string
make_regex = regex_keywords.make_regex
make_regexes = regex_keywords.make_regexes


# TODO: translate to english before we try to apply the keyword matches
# TODO: if event creator has created dance events previously, give it some weight
# TODO: 

# TODO: for each style-keyword, give it some weight. don't be a requirement but yet-another-bayes-input
# TODO: add a bunch of classifier logic
# TODO: for iffy events, assume @ in the title means its a club event. same with monday(s) tuesday(s) etc.
# TODO: house class, house workshop, etc, etc. since 'house' by itself isn't sufficient
# maybe feed keywords into auto-classifying event type? bleh.


battle_keywords = [
    'apache line',
    'battle of the year', 'boty', 'compete',
    'competitions?',
    'konkurrence', # danish competition
    'competencia', # spanish competition
    u'competición', # spanish competition
    u'compétition', # french competition
    u'thi nhảy', # dance competition vietnam
    'kilpailu\w*' # finish competition
    'konkursams', # lithuanian competition
    'verseny', # hungarian competition
    'championships?',
    'champs?',
    u'čempionatams', # lithuanian championship
    'campeonato', # spanish championship
    'meisterschaft', # german championship
    'concorsi', # italian competition
    u'danstävling', # swedish dance competition
    u'แข่งขัน', # thai competition
    'crew battle[sz]?', 'exhibition battle[sz]?',
    'battles?',
    'battlu(?:je)?', # french czech
    u'比賽', # chinese battle
    u'バトル', # japanese battle
    u'битката', # bulgarian battle
    'batallas', # battles spanish
    'zawody', # polish battle/contest
    'walki', # polish battle/fight
    u'walkę', # polish battle/fight
    'bitwa', # polish battle
    u'bitwę', # polish battle
    'bitwach', # polish battle
    u'バトル', # japanese battle
    'tournaments?',
    'tournoi', # french tournament
    u'大会', # japanese tournament
    u'トーナメント', # japanese tournament
    'turnie\w*', # tournament polish/german
    u'giải đấu', # tournament vietnamese
    u'thi đấu', # competition vietnamese
    u'състезанието', # competition bulgarian
    u'đấu', # game vietnamese
    'turneringer', # danish tournament
    'preselections?',
    u'présélections?', # preselections french
    r'(?:seven|7)\W*(?:to|two|2)\W*(?:smoke|smook|somke)',
    'crew\W?v[sz]?\W?crew',
    'bonnie\s*(?:and|&)\s*clyde',
    'prelims?',
    u'初賽', # chinese preliminaries
]


class_keywords = [
    'work\W?shop\W?s?',
    'ws', # japanese workshop WS
    'w\.s\.', # japanese workshop W.S.
    u'ワークショップ', # japanese workshop
    'cursillo', # spanish workshop
    'ateliers', # french workshop
    'workshopy', # czech workshop
    u'סדנאות', # hebrew workshops
    u'סדנה', # hebew workshop
    # 'taller', # workshop spanish
    'delavnice', # workshop slovak
    'talleres', # workshops spanish
    'radionicama', # workshop croatian
    'warsztaty', # polish workshop
    u'warsztatów', # polish workshop
    u'seminarų', # lithuanian workshop
    'taller de', # spanish workshop
    'intensives?',
    'intensivo', # spanish intensive
    'class with', 'master\W?class(?:es)?',
    'company class',
    u'мастер-класса?', # russian master class
    u'классa?', # russian class
    'class(?:es)?', 'lessons?', 'courses?',
    'klass(?:en)?', # slovakian class
    u'수업', # korean class
    u'수업을', # korean classes
    'lekc[ie]', # czech lesson
    u'課程', # course chinese
    u'課', # class chinese
    u'堂課', # lesson chinese
    u'コース', # course japanese
    'concorso', # course italian
    'kurs(?:y|en)?', # course german/polish
    'aulas?', # portuguese class(?:es)?
    u'특강', # korean lecture
    'lektion(?:en)?', # german lecture
    'lekcie', # slovak lessons
    'dansklasser', # swedish dance classes
    'lekcj[ai]', # polish lesson
    'eigoje', # lithuanian course
    'pamokas', # lithuanian lesson
    'kursai', # course lithuanian
    'lez.', #  lesson italian
    'lezione', # lesson italian
    'lezioni', # lessons italian
    u'zajęciach', # class polish
    u'zajęcia', # classes polish
    u'คลาส', # class thai
    'classe', # class italian
    'classi', # classes italin
    'klasser?', # norwegian class
    'cours', 'clases?',
    'camp',
    'kamp',
    'kemp',
    'formazione', # training italian
    'formazioni', # training italian
    u'トレーニング', # japanese training
]

audition_keywords = [
    'try\W?outs?',
    'casting',
     'casting call',
    'castingul', # romanian casting
    'auditions?',
    'audicija', # audition croatia
    'audiciones', # spanish audition
    'konkurz', # audition czech
    u'試鏡', # chinese audition
    'audizione', # italian audition
    'naborem', # polish recruitment/audition
]

event_keywords = [
    'open circles',
    'session', # the plural 'sessions' is handled up above under club-and-event keywords
    u'セッション', # japanese session
    u'練習会', # japanese training
    u'練習', # japanese practice
    'abdc', 'america\W?s best dance crew',
]

english_digit_x_keywords = [
    'v/s',
    r'vs?\.?',
    'on',
    'x',
    u'×',
]
digit_x_keywords = english_digit_x_keywords + [
    'na',
    'mot',
    'contra',
    'contre',
]
digit_x_string = '|'.join(digit_x_keywords)
english_digit_x_string = '|'.join(english_digit_x_keywords)
n_x_n_keywords = [u'%s[ -]?(?:%s)[ -]?%s' % (i, digit_x_string, i) for i in range(12)[1:]]
n_x_n_keywords += [u'%s[ -](?:%s)[ -]%s' % (i, english_digit_x_string, i) for i in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']]
event_keywords += class_keywords
event_keywords += n_x_n_keywords
event_keywords += battle_keywords
event_keywords += audition_keywords
event_keywords += keywords.get(keywords.CYPHER)

judge_keywords = [
    'jurys?',
    'jurados?', # spanish jury
    u'журито', # bulgarian jury
    'judge[sz]?',
    'jures', # french jury
    '(?:les? )?juges?', # french judges
    'giudici', # italian judges
    u'השופט', # hebrew judge
    u'השופטים', # hebrew judges
    u'teisėjai', # lithuanian judges
    'tuomaristo', # jury finnish
    'jueces', # spanish judges
    'juriu', # romanian judges
    'giuria', # jury italian
    u'評審', # chinese judges
    u'評判', # chinese judges
    u'評判團', # chinese judges
    u'審査員', # japanese judges
    u'ジャッジ', # japanese judges
]
event_keywords += judge_keywords


french_event_keywords = [
    'spectacle',
    'stage',
]

italian_event_keywords = [
    'stage',
]

dance_wrong_style_keywords = [
    'styling', 'salsa', 'bachata', 'balboa', 'tango', 'latin', 'lindy', 'lindyhop', 'swing', 'wcs', 'samba',
    'latines', 'quickstep', 'rumba', 'cha\W?cha',
    'blues',
    'waltz',
    'salsy', # salsa czech
    'salser[oa]s?',
    'kizomba',
    'disco dance',
    'disco tan\w+', # czech disco dance
    'milonga',
    'dance partner',
    'cha cha',
    'hula',
    'tumbling',
    'exotic',
    'cheer',
    'barre',
    'butoh',
    'contato improv\w*',
    'contact improv\w*',
    'contratto mimo', # italian contact mime
    'musical theat(?:re|er)',
    'pole danc\w+', 'flirt danc\w+',
    'go\W?go',
    'bollywood', 'kalbeliya', 'bhawai', 'teratali', 'ghumar',
    'indienne',
    'persiana?',
    'arabe', 'arabic', 'araba',
    'oriental\w*', 'oriente', 
    'cubana',
    'capoeira',
    'tahitian dancing',
    'tahitienne',
    'folklor\w+',
    'kizomba',
    'burlesque',
    u'バーレスク', # burlesque japan
    'limon',
    'artist\Win\Wresidence',
    'residency',
    'disciplinary',
    'reflective',
    'clogging',
    'zouk',
    'african dance',
    'afro dance',
    'afro mundo',
    'class?ic[ao]',
    'acroyoga',
    'kirtan',
    'hoop\W?dance',
    'modern dance',
    'pilates',
    'tribal',
    'jazz', 'tap', 'contemporary',
    u'súčasný', # contemporary slovak
    u'współczesnego', # contemporary polish
    'contempor\w*', # contemporary italian, french
    'africa\w+',
    'sabar',
    'aerial silk',
    'silk',
    'aerial',
    'zumba', 'belly\W?danc(?:e(?:rs?)?|ing)', 'bellycraft', 'worldbellydancealliance',
    'soca',
    'flamenco',
    'technique',
    'guest artists?',
    'partnering',
    'charleston',
]
dance_wrong_style_title_keywords = dance_wrong_style_keywords + [
    # Sometimes used in studio name even though it's still a hiphop class:
    'ballroom',
    'ballet',
    'yoga',
    'talent shows?', # we don't care about talent shows that offer dance options
    'stiletto',
    '\w+ball', # basketball/baseball/football tryouts
]

all_regexes = {}

grouped_manual_dance_keywords = {}

INDEPENDENT_KEYWORD = 0
DEPENDENT_KEYWORD = 1

#TODO(lambert): maybe handle 'byronom coxom' in slovakian with these keywords
def get_manual_dance_keywords(filename):
    manual_keywords = []
    dependent_manual_keywords = []
    import os
    if os.getcwd().endswith('mapreduce'): #TODO(lambert): what is going on with appengine sticking me in the wrong starting directory??
        base_dir = '..'
    else:
        base_dir = '.'

    f = codecs.open('%s/dance_keywords/%s.txt' % (base_dir, filename), encoding='utf-8')
    for line in f.readlines():
        line = re.sub('\s*#.*', '', line.strip())
        if not line:
            continue
        if line.endswith(',0'):
            line = line[:-2]
            dependent_manual_keywords.append(line)
        else:
            manual_keywords.append(line)

    result = [None, None]
    result[INDEPENDENT_KEYWORD] = manual_keywords
    result[DEPENDENT_KEYWORD] = dependent_manual_keywords
    return result

manual_keywords = {}
manual_dance_keywords = []
dependent_manual_dance_keywords = []
manual_dancers = []
dependent_manual_dancers = []

def build_regexes():
    global manual_keywords
    global manual_dance_keywords, dependent_manual_dance_keywords
    global manual_dancers, dependent_manual_dancers
    if 'good_capturing_keyword_regex' in all_regexes:
        return

    dancer_keyword_files = ['bboy_crews', 'bboys', 'choreo_crews', 'choreo_dancers', 'freestyle_crews', 'freestyle_dancers']
    extra_keyword_files = ['choreo_keywords', 'freestyle_keywords', 'competitions', 'good_djs']

    for filename in dancer_keyword_files + extra_keyword_files:
        manual_keywords[filename] = get_manual_dance_keywords(filename)
    manual_dancers = []
    dependent_manual_dancers = []
    for filename in dancer_keyword_files:
        manual_dancers += manual_keywords[filename][INDEPENDENT_KEYWORD]
        dependent_manual_dancers += manual_keywords[filename][DEPENDENT_KEYWORD]
    manual_keywords['manual_dancers'] = [None, None]
    manual_keywords['manual_dancers'][INDEPENDENT_KEYWORD] = manual_dancers
    manual_keywords['manual_dancers'][DEPENDENT_KEYWORD] = dependent_manual_dancers

    manual_dance_keywords = manual_dancers[:]
    dependent_manual_dance_keywords = dependent_manual_dancers[:]
    for filename in extra_keyword_files:
        manual_dance_keywords += manual_keywords[filename][INDEPENDENT_KEYWORD]
        dependent_manual_dance_keywords += manual_keywords[filename][DEPENDENT_KEYWORD]
    manual_keywords['manual_dance_keywords'] = [None, None]
    manual_keywords['manual_dance_keywords'][INDEPENDENT_KEYWORD] = manual_dance_keywords
    manual_keywords['manual_dance_keywords'][DEPENDENT_KEYWORD] = dependent_manual_dance_keywords

    for keyword, x in manual_keywords.iteritems():
        if x[INDEPENDENT_KEYWORD]:
            all_regexes['%s_regex' % keyword] = make_regexes(x[INDEPENDENT_KEYWORD])
        else:
            all_regexes['%s_regex' % keyword] = make_regexes(r'NEVER_MATCH_BLAGSDFSDFSEF')
        if x[INDEPENDENT_KEYWORD] + x[DEPENDENT_KEYWORD]:
            all_regexes['extended_%s_regex' % keyword] = make_regexes(x[INDEPENDENT_KEYWORD] + x[DEPENDENT_KEYWORD])
        else:
            all_regexes['%s_regex' % keyword] = make_regexes(r'NEVER_MATCH_BLAGSDFSDFSEF')

    all_regexes['good_keyword_regex']           = make_regexes(keywords.get(keywords.EASY_DANCE, keywords.EASY_EVENT, keywords.EASY_BATTLE, keywords.DANCE, keywords.PRACTICE, keywords.PERFORMANCE, keywords.CONTEST, keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_CHOREO) + event_keywords + manual_dance_keywords + dependent_manual_dance_keywords, wrapper='(?i)%s')
    all_regexes['good_capturing_keyword_regex'] = make_regexes(keywords.get(keywords.EASY_DANCE, keywords.EASY_EVENT, keywords.EASY_BATTLE, keywords.DANCE, keywords.PRACTICE, keywords.PERFORMANCE, keywords.CONTEST, keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_CHOREO) + event_keywords + manual_dance_keywords + dependent_manual_dance_keywords, matching=True, wrapper='(?i)%s')

all_regexes['preprocess_removals_regex'] = keywords.get_regex(keywords.PREPROCESS_REMOVAL)
all_regexes['dance_wrong_style_regex'] = make_regexes(dance_wrong_style_keywords)
all_regexes['judge_keywords_regex'] = make_regexes(judge_keywords)
all_regexes['audition_regex'] = make_regexes(audition_keywords)
all_regexes['battle_regex'] = make_regexes(battle_keywords)
all_regexes['n_x_n_regex'] = make_regexes(n_x_n_keywords)
all_regexes['dance_wrong_style_title_regex'] = make_regexes(dance_wrong_style_title_keywords)
all_regexes['dance_and_music_regex'] = keywords.get_regex(keywords.AMBIGUOUS_DANCE_MUSIC)
all_regexes['class_regex'] = make_regexes(class_keywords)
all_regexes['club_and_event_regex'] = make_regexes(keywords.get(keywords.PRACTICE, keywords.PERFORMANCE, keywords.CONTEST))
all_regexes['easy_choreography_regex'] = keywords.get_regex(keywords.EASY_CHOREO)
all_regexes['club_only_regex'] = make_regexes(keywords.CLUB_ONLY)

all_regexes['easy_dance_regex'] = keywords.get_regex(keywords.EASY_DANCE)
all_regexes['easy_event_regex'] = make_regexes(keywords.get(keywords.EASY_EVENT, keywords.EASY_BATTLE))
all_regexes['dance_regex'] = keywords.get_regex(keywords.DANCE)
all_regexes['event_regex'] = make_regexes(event_keywords)
all_regexes['french_event_regex'] = make_regexes(event_keywords + french_event_keywords)
all_regexes['italian_event_regex'] = make_regexes(event_keywords + italian_event_keywords)

all_regexes['bad_capturing_keyword_regex'] = make_regexes(keywords.get(keywords.CLUB_ONLY) + dance_wrong_style_keywords, matching=True)

all_regexes['italian'] = make_regexes(['di', 'i', 'e', 'con'])
all_regexes['french'] = make_regexes(["l'\w*", 'le', 'et', 'une', 'avec', u'à', 'pour'])

# NOTE: Eventually we can extend this with more intelligent heuristics, trained models, etc, based on multiple keyword weights, names of teachers and crews and whatnot

def get_relevant_text(fb_event):
    # use a separator here, so 'actors workshop' 'breaking boundaries...' doesn't match 'workshop breaking'
    search_text = (fb_event['info'].get('name', '') + ' . . . . ' + fb_event['info'].get('description', '')).lower()
    return search_text

class ClassifiedEvent(object):
    def __init__(self, fb_event, language=None):
        self.fb_event = fb_event
        if 'name' not in fb_event['info']:
            logging.info("fb event id is %s has no name, with value %s", fb_event['info']['id'], fb_event)
            self.search_text = ''
            self.title = ''
        else:
            self.search_text = get_relevant_text(fb_event)
            self.title = fb_event['info'].get('name', '').lower()
        self.language = language
        self.times = {}
        self.token_originals = collections.defaultdict(lambda: [])
        self.tokenized_text = self.search_text

    def classify(self):
        build_regexes()

        #self.language not in ['ja', 'ko', 'zh-CN', 'zh-TW', 'th']:
        if cjk_detect.cjk_regex.search(self.search_text):
            cjk_chars = len(cjk_detect.cjk_regex.findall(self.search_text))
            if 1.0 * cjk_chars / len(self.search_text) > 0.05:
                self.boundaries = regex_keywords.NO_WORD_BOUNDARIES
            else:
                self.boundaries = regex_keywords.WORD_BOUNDARIES
        else:
            self.boundaries = regex_keywords.WORD_BOUNDARIES
        idx = self.boundaries

        self.final_search_text = all_regexes['preprocess_removals_regex'][idx].sub('', self.search_text)
        search_text = self.final_search_text
        self.final_title = all_regexes['preprocess_removals_regex'][idx].sub('', self.title)
        title = self.final_title

        #if not all_regexes['good_keyword_regex'][idx].search(search_text):
        #    self.dance_event = False
        #    return
        a = time.time()
        b = time.time()
        self.manual_dance_keywords_matches = all_regexes['manual_dance_keywords_regex'][idx].findall(search_text)
        self.times['manual_regex'] = time.time() - b
        easy_dance_matches = all_regexes['easy_dance_regex'][idx].findall(search_text)
        easy_event_matches = all_regexes['easy_event_regex'][idx].findall(search_text)
        self.real_dance_matches = all_regexes['dance_regex'][idx].findall(search_text)
        if all_regexes['french'][idx].search(search_text):
            event_matches = all_regexes['french_event_regex'][idx].findall(search_text)
        elif all_regexes['italian'][idx].search(search_text):
            event_matches = all_regexes['italian_event_regex'][idx].findall(search_text)
        else:
            event_matches = all_regexes['event_regex'][idx].findall(search_text)
        dance_wrong_style_matches = all_regexes['dance_wrong_style_regex'][idx].findall(search_text)
        dance_and_music_matches = all_regexes['dance_and_music_regex'][idx].findall(search_text)
        club_and_event_matches = all_regexes['club_and_event_regex'][idx].findall(search_text)
        easy_choreography_matches = all_regexes['easy_choreography_regex'][idx].findall(search_text)
        club_only_matches = all_regexes['club_only_regex'][idx].findall(search_text)
        self.times['all_regexes'] = time.time() - a

        self.found_dance_matches = self.real_dance_matches + easy_dance_matches + dance_and_music_matches + self.manual_dance_keywords_matches + easy_choreography_matches
        self.found_event_matches = event_matches + easy_event_matches + club_and_event_matches
        self.found_wrong_matches = dance_wrong_style_matches + club_only_matches

        title_wrong_style_matches = all_regexes['dance_wrong_style_regex'][idx].findall(title)
        title_good_matches = all_regexes['good_keyword_regex'][idx].findall(title)
            
        combined_matches = self.found_dance_matches + self.found_event_matches
        words = re.split(r'\W+', re.sub(r'\bhttp.*?\s', '', search_text))
        fraction_matched = 1.0 * len(combined_matches) / len(words)
        if not fraction_matched:
            self.calc_inverse_keyword_density = 100
        else:
            self.calc_inverse_keyword_density = -int(math.log(fraction_matched, 2))

        #strong = 0
        #for line in search_text.split('\n'):
        #    matches = all_regexes['good_keyword_regex'][idx].findall(line)
        #    good_parts = sum(len(x) for x in matches)
        #    if 1.0 * good_parts / len(line) > 0.1:
        #        # strong!
        #        strong += 1
        
        if len(self.manual_dance_keywords_matches) >= 1:
            self.dance_event = 'obvious dancer or dance crew or battle'
        # one critical dance keyword
        elif len(self.real_dance_matches) >= 1:
            self.dance_event = 'obvious dance style'
        # If the title has a bad-style and no good-styles, mark it bad
        elif (all_regexes['dance_wrong_style_title_regex'][idx].search(title) and
            not (
                all_regexes['dance_and_music_regex'][idx].search(title) or
                self.manual_dance_keywords_matches or
                self.real_dance_matches)): # these two are implied by the above, but do it here just in case future clause re-ordering occurs
            self.dance_event = False

        elif len(dance_and_music_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1 and self.calc_inverse_keyword_density < 5 and not (title_wrong_style_matches and not title_good_matches):
            self.dance_event = 'hiphop/funk and good event type'
        # one critical event and a basic dance keyword and not a wrong-dance-style and not a generic-club
        elif len(easy_dance_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1 and len(dance_wrong_style_matches) == 0 and self.calc_inverse_keyword_density < 5:
            self.dance_event = 'dance event thats not a bad-style'
        elif len(easy_dance_matches) >= 1 and len(club_and_event_matches) >= 1 and len(dance_wrong_style_matches) == 0 and len(club_only_matches) == 0:
            self.dance_event = 'dance show thats not a club'
        else:
            self.dance_event = False
        self.times['all_match'] = time.time() - a


    def replace_tokens(self, token):
        def replace_with(match):
            matched_text = match.group(0)
            self.token_originals[token].append(matched_text)
            return token
        self.tokenized_text = keywords.get_regex(token)[self.boundaries].sub(replace_with, self.tokenized_text)

    def count_tokens(self, token):
        return len(self.token_originals[token])
        
    def get_tokens(self, token):
        return self.token_originals[token]
        
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
    def inverse_keyword_density(self):
        return self.calc_inverse_keyword_density


def get_classified_event(fb_event, language=None):
    classified_event = ClassifiedEvent(fb_event, language)
    classified_event.classify()
    return classified_event

def relevant_keywords(fb_event):
    build_regexes()
    text = get_relevant_text(fb_event)
    if cjk_detect.cjk_regex.search(text):
        idx = regex_keywords.NO_WORD_BOUNDARIES
    else:
        idx = regex_keywords.WORD_BOUNDARIES
    good_keywords = all_regexes['good_capturing_keyword_regex'][idx].findall(text)
    bad_keywords = all_regexes['bad_capturing_keyword_regex'][idx].findall(text)
    return sorted(set(good_keywords).union(bad_keywords))

@skip_filter
def highlight_keywords(text):
    build_regexes()
    if cjk_detect.cjk_regex.search(text):
        idx = regex_keywords.NO_WORD_BOUNDARIES
    else:
        idx = regex_keywords.WORD_BOUNDARIES
    text = all_regexes['good_capturing_keyword_regex'][idx].sub('<span class="matched-text">\\1</span>', text)
    text = all_regexes['bad_capturing_keyword_regex'][idx].sub('<span class="bad-matched-text">\\1</span>', text)
    return text

if __name__ == '__main__':
    a = ['club', 'bottle service', 'table service', 'coat check', 'free before', 'vip', 'guest\\W?list', 'drink specials?', 'resident dj\\W?s?', 'dj\\W?s?', 'techno', 'trance', 'indie', 'glitch', 'bands?', 'dress to', 'mixtape', 'decks', 'r&b', 'local dj\\W?s?', 'all night', 'lounge', 'live performances?', 'doors', 'restaurant', 'hotel', 'music shows?', 'a night of', 'dance floor', 'beer', 'blues', 'bartenders?', 'waiters?', 'waitress(?:es)?', 'go\\Wgo', 'gogo', 'styling', 'salsa', 'bachata', 'balboa', 'tango', 'latin', 'lindy', 'lindyhop', 'swing', 'wcs', 'samba', 'waltz', 'salsy', 'milonga', 'dance partner', 'cha cha', 'hula', 'tumbling', 'exotic', 'cheer', 'barre', 'contact improv', 'contact improv\\w*', 'contratto mimo', 'musical theat(?:re|er)', 'pole dance', 'flirt dance', 'bollywood', 'kalbeliya', 'bhawai', 'teratali', 'ghumar', 'indienne', 'persiana?', 'arabe', 'arabic', 'oriental\\w*', 'oriente', 'cubana', 'capoeira', 'tahitian dancing', 'folklor\\w+', 'kizomba', 'burlesque', 'technique', 'limon', 'clogging', 'zouk', 'afro mundo', 'class?ic[ao]', 'acroyoga', 'kirtan', 'modern dance', 'pilates', 'tribal', 'jazz', 'tap', 'contemporary', 'contempor\\w*', 'africa\\w+', 'sabar', 'silk', 'aerial', 'zumba', 'belly\\W?danc(?:e(?:rs?)?|ing)', 'bellycraft', 'worldbellydancealliance', 'soca', 'flamenco']
    a = sorted(a)
    print a
    print highlight_keywords(u' ๆ ซึ่งไม่ให้พี่น้อง Bboy ได้ผิดหวังอีกต่อไป*')
    print highlight_keywords('matched-text')
