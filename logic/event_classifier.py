# -*-*- encoding: utf-8 -*-*-

import codecs
import collections
import itertools
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
from logic import rules

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

manual_dancer_keyword = None
manual_dance_keyword = None

def build_regexes():
    global manual_keywords
    global manual_dance_keywords, dependent_manual_dance_keywords
    global manual_dancers, dependent_manual_dancers
    global manual_dancer_keyword, manual_dance_keyword
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
    # TODO: rename, put in a useful place, etc
    manual_dancer_keyword = keywords.token('MANUALDANCER')
    keywords.add(manual_dancer_keyword, manual_keywords['manual_dancers'][INDEPENDENT_KEYWORD])

    manual_dance_keywords = manual_dancers[:]
    dependent_manual_dance_keywords = dependent_manual_dancers[:]
    for filename in extra_keyword_files:
        manual_dance_keywords += manual_keywords[filename][INDEPENDENT_KEYWORD]
        dependent_manual_dance_keywords += manual_keywords[filename][DEPENDENT_KEYWORD]
    manual_keywords['manual_dance_keywords'] = [None, None]
    manual_keywords['manual_dance_keywords'][INDEPENDENT_KEYWORD] = manual_dance_keywords + ['_MANUALDANCER\d*_']
    manual_keywords['manual_dance_keywords'][DEPENDENT_KEYWORD] = dependent_manual_dance_keywords
    #manual_dance_keyword = keywords.token('MANUAL_DANCE')
    #keywords.add(manual_dance_keyword, manual_keywords['manual_dance_keywords'][INDEPENDENT_KEYWORD])

    for keyword, x in manual_keywords.iteritems():
        if x[INDEPENDENT_KEYWORD]:
            all_regexes['%s_regex' % keyword] = make_regexes(x[INDEPENDENT_KEYWORD])
        else:
            all_regexes['%s_regex' % keyword] = make_regexes(r'NEVER_MATCH_BLAGSDFSDFSEF')
        if x[INDEPENDENT_KEYWORD] + x[DEPENDENT_KEYWORD]:
            all_regexes['extended_%s_regex' % keyword] = make_regexes(x[INDEPENDENT_KEYWORD] + x[DEPENDENT_KEYWORD])
        else:
            all_regexes['extended_%s_regex' % keyword] = make_regexes(r'NEVER_MATCH_BLAGSDFSDFSEF')

    good_keywords = keywords.get(
        keywords.EASY_DANCE,
        keywords.EASY_EVENT,
        keywords.EASY_BATTLE,
        keywords.DANCE,
        keywords.PRACTICE,
        keywords.PERFORMANCE,
        keywords.CONTEST,
        keywords.AMBIGUOUS_DANCE_MUSIC,
        keywords.EASY_CHOREO,
        keywords.CLASS,
        keywords.N_X_N,
        keywords.BATTLE,
        keywords.OBVIOUS_BATTLE,
        keywords.AUDITION,
        keywords.CYPHER,
        keywords.JUDGE
    ) + manual_dance_keywords + dependent_manual_dance_keywords
    all_regexes['good_keyword_regex'] = make_regexes(good_keywords, wrapper='(?i)%s')
    all_regexes['good_capturing_keyword_regex'] = make_regexes(good_keywords, matching=True, wrapper='(?i)%s')

all_regexes['dance_wrong_style_title_regex'] = regex_keywords.make_regexes_raw(rules.get(rules.DANCE_WRONG_STYLE_TITLE).as_expanded_regex())

all_regexes['bad_capturing_keyword_regex'] = make_regexes(keywords.get(keywords.CLUB_ONLY, keywords.DANCE_WRONG_STYLE), matching=True)

all_regexes['romance'] = make_regexes([
    'di', 'i', 'e', 'con', # italian
    "l'\w*", 'le', 'et', 'une', 'avec', u'à', 'pour', # french
])

# NOTE: Eventually we can extend this with more intelligent heuristics, trained models, etc, based on multiple keyword weights, names of teachers and crews and whatnot

def get_relevant_text(fb_event):
    # use a separator here, so 'actors workshop' 'breaking boundaries...' doesn't match 'workshop breaking'
    search_text = (fb_event['info'].get('name', '') + ' . . . . ' + fb_event['info'].get('description', '')).lower()
    return search_text


def _flatten(listOfLists):
    "Flatten one level of nesting"
    return list(itertools.chain.from_iterable(listOfLists))

_rule_regexes = {}
def get_rule_regex(rule, **kwargs):
    key = (rule, tuple(sorted(kwargs.items())))
    if key not in _rule_regexes:
        _rule_regexes[key] = regex_keywords.make_regexes_raw(rules.get(rule).as_expanded_regex(), **kwargs)
    return _rule_regexes[key]

class StringProcessor(object):
    def __init__(self, text, match_on_word_boundaries):
        self.text = text
        self.match_on_word_boundaries = match_on_word_boundaries
        self.token_originals = collections.defaultdict(lambda: 0)

    def tokenize_all(self, *tokens):
        for token in tokens:
            self.tokenize(token)

    def tokenize(self, token):
        """Tokenizes the relevant bits of this String. Replaces all instances of the token's regex, with the token's string representation.
        """
        # Don't actually tokenize most things, turns out there's no runtime performance advantage, and a quality hit.
        return
        # I tried a bunch of implementations for speed here. This approach appears to be the fastest:
        # Run tokenize for each regex, doing a brute force search-and-replace on the string. (+70sec)
        # We used to include a lambda-replace function to grab the contents, but later realized the original matched string is irrelevant to our use cases.
        #
        # Other ideas that didn't work included:
        # - Do this as a matching-regex with one match group per token, to figure out which token matched. (+waaaay to slow)
        # - In a non-matching regex, but with the matched text, run a matching-regex to figure out which token matched. (+150sec)
        # - In a non-matching regex, but with the matched text, run each token regex by hand to see which matched. (+100sec)
        # - Do one pass for findall to get tokens, and another for sub to replace with the magic token. (+100sec)
        # Could have explored O(lgN) search options for a couple of the above, but it felt like the overhead of entering/exiting re2 was the biggest cost.

    def real_tokenize(self, token):
        def word_with_hash(match):
            return token.replace_string(match.group(0))
        self.text, count = keywords.get_regex(token)[self.match_on_word_boundaries].subn(word_with_hash, self.text)
        # If we want to get the matched results/keywords too, then we should only do that conditinoally on count, here:
        #if count:
        #    self.token_originals[token].extend(keywords.get_regex(token)[self.match_on_word_boundaries].findall(self.text))

    def count_tokens(self, token):
        return len(self._get_token(token))

    def _get_token(self, token):
        if token not in self.token_originals:
            self.token_originals[token] = keywords.get_regex(token)[self.match_on_word_boundaries].findall(self.text)
        return self.token_originals[token]

    def get_tokens(self, *tokens):
        return _flatten(self._get_token(token) for token in tokens)

    def get_tokenized_text(self):
        return self.text

    def find_with_rule(self, rule, **kwargs):
        regex = get_rule_regex(rule, **kwargs)
        return regex[self.match_on_word_boundaries].findall(self.text)

    def delete_with_rule(self, rule, **kwargs):
        regex = get_rule_regex(rule, **kwargs)
        trimmed_text = regex[self.match_on_word_boundaries].sub('', self.text)
        return StringProcessor(trimmed_text, self.match_on_word_boundaries)

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

        self.processed_text = StringProcessor(self.search_text, self.boundaries)
        # This must be first, to remove the fake keywords
        self.processed_text.tokenize(keywords.PREPROCESS_REMOVAL)
        self.processed_text.real_tokenize(keywords.PREPROCESS_REMOVAL)
        self.processed_text.real_tokenize(manual_dancer_keyword)
        self.processed_text.real_tokenize(keywords.GOOD_INSTANCE_OF_BAD_CLUB)
        self.processed_text.real_tokenize(keywords.DANCE)

        self.final_search_text = self.processed_text.get_tokenized_text()
        search_text = self.final_search_text

        # Then we apply a bunch of our regular keyword rules
        # Not CONNECTOR, not PREPROCESS_REMOVAL.
        # There are some overlapping keywords in here that I need to fix. Maybe can automate detection with a master-replace-regex that looks in these, to find what to replace with (and errors on multiple)
        # But in the meantime, let's start to figure out a rough ordering for them. dance at the bottom, good-instance-of-bad-club hack at the top, etc. Hopefully the middle tier can be large and order-irrelevant.
        desired_keywords = [
            manual_dancer_keyword,
            keywords.GOOD_INSTANCE_OF_BAD_CLUB,

            keywords.DANCE, #jazzfunk, streetjazz, etc

            keywords.CLASS,
            keywords.N_X_N,
            keywords.BATTLE,
            keywords.OBVIOUS_BATTLE,
            keywords.AUDITION,
            keywords.CYPHER,
            keywords.JUDGE,

            # king-of-the must be before king
            keywords.KING_OF_THE,
            keywords.KING,

            keywords.AMBIGUOUS_CLASS,
            keywords.AMBIGUOUS_DANCE_MUSIC,
            keywords.AMBIGUOUS_WRONG_STYLE,
            keywords.BAD_CLUB,
            keywords.BONNIE_AND_CLYDE,
            keywords.CLUB_ONLY,
            keywords.CONTEST,
            keywords.DANCE_WRONG_STYLE,
            keywords.EVENT,
            keywords.FORMAT_TYPE,
            keywords.FREESTYLE,
            keywords.HOUSE,
            keywords.OTHER_SHOW,
            keywords.PERFORMANCE,
            keywords.PRACTICE,
            keywords.STREET,
            keywords.VOGUE,
            keywords.WRONG_AUDITION,
            keywords.WRONG_BATTLE,
            keywords.WRONG_BATTLE_STYLE,
            keywords.WRONG_NUMBERED_LIST,

            #keywords.SEMI_BAD_DANCE,

            keywords.EASY_BATTLE,
            keywords.EASY_CHOREO,
            keywords.EASY_DANCE,
            keywords.EASY_EVENT,
            keywords.EASY_VOGUE,
        ]
        for keyword in desired_keywords:
            self.processed_text.tokenize(keyword)

        self.processed_title = StringProcessor(self.title, self.boundaries)
        self.processed_title.tokenize(keywords.PREPROCESS_REMOVAL)
        self.processed_title.real_tokenize(keywords.PREPROCESS_REMOVAL)
        self.final_title = self.processed_title.get_tokenized_text()
        title = self.final_title

        for keyword in desired_keywords:
            self.processed_title.tokenize(keyword)
        for keyword in [
            keywords.BAD_COMPETITION_TITLE_ONLY,
            keywords.DANCE_WRONG_STYLE_TITLE_ONLY,
        ]:
            self.processed_title.tokenize(keyword)

        #if not all_regexes['good_keyword_regex'][idx].search(search_text):
        #    self.dance_event = False
        #    return
        a = time.time()
        b = time.time()
        self.manual_dance_keywords_matches = all_regexes['manual_dance_keywords_regex'][idx].findall(search_text)
        self.times['manual_regex'] = time.time() - b
        self.real_dance_matches = self.processed_text.find_with_rule(rules.GOOD_DANCE)
        if all_regexes['romance'][idx].search(search_text):
            event_matches = self.processed_text.find_with_rule(rules.EVENT_WITH_ROMANCE_EVENT)
        else:
            event_matches = self.processed_text.find_with_rule(rules.EVENT)
        club_and_event_matches = self.processed_text.get_tokens(keywords.PRACTICE, keywords.PERFORMANCE, keywords.CONTEST)
        self.times['all_regexes'] = time.time() - a

        self.found_dance_matches = self.real_dance_matches + self.processed_text.get_tokens(keywords.EASY_DANCE, keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_CHOREO) + self.manual_dance_keywords_matches
        self.found_event_matches = event_matches + self.processed_text.get_tokens(keywords.EASY_EVENT, keywords.EASY_BATTLE) + club_and_event_matches
        self.found_wrong_matches = self.processed_text.get_tokens(keywords.DANCE_WRONG_STYLE) + self.processed_text.get_tokens(keywords.CLUB_ONLY)

        title_wrong_style_matches = all_regexes['dance_wrong_style_title_regex'][idx].findall(title)
        title_good_matches = all_regexes['good_keyword_regex'][idx].findall(title)
        combined_matches_string = ' '.join(self.found_dance_matches + self.found_event_matches)
        dummy, combined_matches = re.subn(r'\w+', '', combined_matches_string)
        dummy, words = re.subn(r'\w+', '', re.sub(r'\bhttp.*?\s', '', search_text))
        fraction_matched = 1.0 * (combined_matches+1) / (words+1)
        if not fraction_matched:
            self.calc_inverse_keyword_density = 100
        else:
            self.calc_inverse_keyword_density = -math.log(fraction_matched, 2)

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
                self.processed_title.get_tokens(keywords.AMBIGUOUS_DANCE_MUSIC) or
                self.manual_dance_keywords_matches or
                self.real_dance_matches)): # these two are implied by the above, but do it here just in case future clause re-ordering occurs
            self.dance_event = False

        elif self.processed_text.count_tokens(keywords.AMBIGUOUS_DANCE_MUSIC) >= 1 and (len(event_matches) + self.processed_text.count_tokens(keywords.EASY_CHOREO)) >= 1 and self.calc_inverse_keyword_density < 5 and not (title_wrong_style_matches and not title_good_matches):
            self.dance_event = 'hiphop/funk and good event type'
        # one critical event and a basic dance keyword and not a wrong-dance-style and not a generic-club
        elif self.processed_text.count_tokens(keywords.EASY_DANCE) >= 1 and (len(event_matches) + self.processed_text.count_tokens(keywords.EASY_CHOREO)) >= 1 and not self.processed_text.count_tokens(keywords.DANCE_WRONG_STYLE) and self.calc_inverse_keyword_density < 5:
            self.dance_event = 'dance event thats not a bad-style'
        elif self.processed_text.count_tokens(keywords.EASY_DANCE) >= 1 and len(club_and_event_matches) >= 1 and not self.processed_text.count_tokens(keywords.DANCE_WRONG_STYLE) and self.processed_text.count_tokens(keywords.CLUB_ONLY) == 0:
            self.dance_event = 'dance show thats not a club'
        else:
            self.dance_event = False
        self.times['all_match'] = time.time() - a

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
