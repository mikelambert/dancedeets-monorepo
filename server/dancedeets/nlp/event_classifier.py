# -*-*- encoding: utf-8 -*-*-

import itertools
import logging
import math
try:
    import re2
    import re2 as re
except ImportError as e:
    logging.info("Could not import re2, falling back to re: %s", e)
    re2 = None
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)
import time
from . import cjk_detect
from . import grammar
from . import regex_keywords
from .street import keywords
from .street import rules

from ..util import dates

USE_UNICODE = False

# TODO: translate to english before we try to apply the keyword matches
# TODO: if event creator has created dance events previously, give it some weight
# TODO:

# TODO: for each style-keyword, give it some weight. don't be a requirement but yet-another-bayes-input
# TODO: add a bunch of classifier logic
# TODO: for iffy events, assume @ in the title means its a club event. same with monday(s) tuesday(s) etc.
# TODO: house class, house workshop, etc, etc. since 'house' by itself isn't sufficient
# maybe feed keywords into auto-classifying event type? bleh.

# NOTE: Eventually we can extend this with more intelligent heuristics, trained models, etc, based on multiple keyword weights, names of teachers and crews and whatnot


def _name(obj):
    prop = 'name'
    if hasattr(obj, prop):
        return getattr(obj, prop)
    else:
        return obj['info'].get(prop, '')


def _desc(obj):
    prop = 'description'
    if hasattr(obj, prop):
        return getattr(obj, prop)
    else:
        return obj['info'].get(prop, '')


def get_relevant_text(event):
    # use a separator here, so 'actors workshop' 'breaking boundaries...' doesn't match 'workshop breaking'
    search_text = _name(event) + ' . . . . ' + _desc(event).lower()
    return search_text


def _flatten(listOfLists):
    "Flatten one level of nesting"
    return list(itertools.chain.from_iterable(listOfLists))


class StringProcessor(object):
    def __init__(self, text, match_on_word_boundaries=None, lowercase=True):
        self.text = text.lower() if lowercase else text
        if match_on_word_boundaries is not None:
            self.match_on_word_boundaries = match_on_word_boundaries
        else:
            if cjk_detect.cjk_regex.search(text):
                self.match_on_word_boundaries = regex_keywords.NO_WORD_BOUNDARIES
            else:
                self.match_on_word_boundaries = regex_keywords.WORD_BOUNDARIES
        self._get_token_cache = {}
        self._has_token_cache = {}

    def __repr__(self):
        return 'StringProcessor(%r)' % self.text

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

    def replace_with(self, token, replace_func, flags=0):
        self.text, count = token.hack_double_regex(flags=flags)[self.match_on_word_boundaries].subn(replace_func, self.text)
        return self.text, count

    def real_tokenize(self, token):
        def word_with_hash(match):
            return token.replace_string(match.group(0))

        _, count = self.replace_with(token, word_with_hash)
        # If we want to get the matched results/keywords too, then we should only do that conditinoally on count, here:
        #if count:
        #    self._get_token_cache[token].extend(token.hack_double_regex()[self.match_on_word_boundaries].findall(self.text))

    def has_token(self, token):
        if token not in self._has_token_cache:
            if token in self._get_token_cache:
                if self._get_token_cache[token]:
                    self._has_token_cache[token] = self._get_token_cache[token][0]
                else:
                    self._has_token_cache[token] = None
            else:
                match = token.hack_double_regex()[self.match_on_word_boundaries].search(self.text)
                if match:
                    self._has_token_cache[token] = match.group(0)
                else:
                    self._has_token_cache[token] = None
        return self._has_token_cache[token]

    def count_tokens(self, token):
        _, count = token.hack_double_regex()[self.match_on_word_boundaries].subn('', self.text)
        return count

    def _get_token(self, token):
        if token not in self._get_token_cache:
            self._get_token_cache[token] = token.hack_double_regex()[self.match_on_word_boundaries].findall(self.text)
        return self._get_token_cache[token]

    def get_tokens(self, *tokens):
        # This is an optimization that saves us 1+ second per 10K runs
        if len(tokens) == 1:
            return self._get_token(tokens[0])
        else:
            return _flatten([self._get_token(token) for token in tokens])

    def get_tokenized_text(self):
        return self.text

    def delete_with_rule(self, rule):
        regexes = rule.hack_double_regex()
        trimmed_text = regexes[self.match_on_word_boundaries].sub('', self.text)
        return StringProcessor(trimmed_text, self.match_on_word_boundaries, lowercase=False)


def classified_event_from_fb_event(fb_event, language=None):
    return ClassifiedEvent(
        fb_event,
        fb_event['info'].get('name', ''),
        fb_event['info'].get('description', ''),
        dates.parse_fb_start_time(fb_event),
        dates.parse_fb_end_time(fb_event),
        language=language
    )


class ClassifiedEvent(object):
    def __init__(self, fb_event, name, description, start_time, end_time, language=None):
        self.fb_event = fb_event
        self.title = name.lower()
        # use a separator here, so 'actors workshop' 'breaking boundaries...' doesn't match 'workshop breaking'
        self.search_text = ('%s . . . . %s' % (name, description)).lower()
        self.start_time = start_time
        self.end_time = end_time
        self.language = language
        self.times = {}

    def classify(self):
        #self.language not in ['ja', 'ko', 'zh-CN', 'zh-TW', 'th']:
        if cjk_detect.cjk_regex.search(self.search_text):
            cjk_chars = len(cjk_detect.cjk_regex.findall(self.search_text))
            if 1.0 * cjk_chars / len(self.search_text) > 0.05:
                self.boundaries = regex_keywords.NO_WORD_BOUNDARIES
            else:
                self.boundaries = regex_keywords.WORD_BOUNDARIES
        else:
            self.boundaries = regex_keywords.WORD_BOUNDARIES

        self.processed_text = StringProcessor(self.search_text, self.boundaries)
        # This must be first, to remove the fake keywords
        self.processed_text.real_tokenize(keywords.PREPROCESS_REMOVAL)

        # Running real_tokenize() on a rule replaces it with the name of the high-level rule.
        # Instead, let's grab the contents of the rule, which will assume is an Any(), and run on each of the Any()
        manual_dancer = rules.MANUAL_DANCER[grammar.STRONG]
        assert isinstance(manual_dancer, grammar.Name)
        assert isinstance(manual_dancer, grammar.Name)
        assert len(manual_dancer.children()) == 1
        assert isinstance(manual_dancer.children()[0], rules.Any)
        manual_dancer_children = manual_dancer.children()[0].children()
        for rule in manual_dancer_children:
            self.processed_text.real_tokenize(rule)

        self.processed_text.real_tokenize(keywords.GOOD_INSTANCE_OF_BAD_CLUB)
        #TODO(lambert): These grab things that are good, and keep them good, so they can't be stolen by other things.
        # Removing them appears to drop us from 9132 true positives down to 9108 true positives.
        # Maybe we can investigate exactly what's going on, and reduce the number of real_tokenize calls needed?
        self.processed_text.real_tokenize(keywords.DANCE)
        self.processed_text.real_tokenize(keywords.STYLE_BREAK)
        self.processed_text.real_tokenize(keywords.STYLE_ROCK)
        self.processed_text.real_tokenize(keywords.STYLE_POP)
        self.processed_text.real_tokenize(keywords.STYLE_LOCK)
        self.processed_text.real_tokenize(keywords.STYLE_WAACK)
        self.processed_text.real_tokenize(keywords.STYLE_HIPHOP)
        self.processed_text.real_tokenize(keywords.STYLE_HOUSE)
        self.processed_text.real_tokenize(keywords.STYLE_DANCEHALL)
        self.processed_text.real_tokenize(keywords.STYLE_KRUMP)
        self.processed_text.real_tokenize(keywords.STYLE_TURF)
        self.processed_text.real_tokenize(keywords.STYLE_LITEFEET)
        self.processed_text.real_tokenize(keywords.STYLE_FLEX)
        self.processed_text.real_tokenize(keywords.STYLE_BEBOP)
        self.processed_text.real_tokenize(keywords.STYLE_ALLSTYLE)

        self.final_search_text = self.processed_text.get_tokenized_text()

        # Or if there are bad keywords, lets see if we can find good keywords on a short line
        short_lines = [line for line in self.final_search_text.split('\n') if len(line) > 500]
        self.processed_short_lines = StringProcessor('\n'.join(short_lines), self.boundaries)

        search_text = self.final_search_text

        self.processed_title = StringProcessor(self.title, self.boundaries)
        self.processed_title.real_tokenize(keywords.PREPROCESS_REMOVAL)
        self.final_title = self.processed_title.get_tokenized_text()

        #if not self.processed_text.get_tokens(rules.ANY_GOOD):
        #    self.dance_event = False
        #    return
        a = time.time()
        b = time.time()
        self.manual_dance_keywords_matches = self.processed_text.get_tokens(rules.MANUAL_DANCE[grammar.STRONG])
        self.times['manual_regex'] = time.time() - b
        self.real_dance_matches = self.processed_text.get_tokens(rules.GOOD_DANCE)
        if self.processed_text.get_tokens(keywords.ROMANCE):
            event_matches = self.processed_text.get_tokens(rules.EVENT_WITH_ROMANCE_EVENT)
        else:
            event_matches = self.processed_text.get_tokens(rules.EVENT)
        club_and_event_matches = self.processed_text.get_tokens(keywords.PRACTICE, keywords.PERFORMANCE, keywords.CONTEST)
        self.times['all_regexes'] = time.time() - a

        self.found_dance_matches = self.real_dance_matches + self.processed_text.get_tokens(
            keywords.EASY_DANCE, keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_CHOREO, keywords.HOUSE, keywords.TOO_EASY_VOGUE,
            keywords.EASY_VOGUE
        ) + self.manual_dance_keywords_matches
        self.found_event_matches = event_matches + self.processed_text.get_tokens(
            keywords.EASY_EVENT, keywords.JAM
        ) + club_and_event_matches
        self.found_wrong_matches = self.processed_text.get_tokens(keywords.DANCE_WRONG_STYLE
                                                                 ) + self.processed_text.get_tokens(keywords.CLUB_ONLY)

        title_wrong_style_matches = self.processed_title.get_tokens(rules.DANCE_WRONG_STYLE_TITLE)
        title_good_matches = self.processed_title.get_tokens(rules.ANY_GOOD)
        combined_matches_string = ' '.join(self.found_dance_matches + self.found_event_matches)
        dummy, combined_matches = re.subn(r'\w+', '', combined_matches_string)
        dummy, words = re.subn(r'\w+', '', re.sub(r'\bhttp.*?\s', '', search_text))
        fraction_matched = 1.0 * (combined_matches + 1) / (words + 1)
        if not fraction_matched:
            self.calc_inverse_keyword_density = 100
        else:
            self.calc_inverse_keyword_density = -math.log(fraction_matched, 2)

        #print self.processed_text.count_tokens(keywords.EASY_DANCE)
        #print len(club_and_event_matches)
        #print self.processed_text.count_tokens(keywords.DANCE_WRONG_STYLE)
        #print self.processed_text.count_tokens(keywords.CLUB_ONLY)
        #strong = 0
        #for line in search_text.split('\n'):
        #   proc_line = f(line)
        #    matches = proc_line.get_tokens(rules.ANY_GOOD)
        #    good_parts = sum(len(x) for x in matches)
        #    if 1.0 * good_parts / len(line) > 0.1:
        #        # strong!
        #        strong += 1
        music_or_dance_keywords = self.processed_text.count_tokens(keywords.AMBIGUOUS_DANCE_MUSIC
                                                                  ) + self.processed_text.count_tokens(keywords.HOUSE)
        if len(self.manual_dance_keywords_matches) >= 1:
            self.dance_event = 'obvious dancer or dance crew or battle'
        # one critical dance keyword
        elif len(self.real_dance_matches) >= 1:
            self.dance_event = 'obvious dance style'
        # If the title has a bad-style and no good-styles, mark it bad
        elif (
            title_wrong_style_matches and not (
                self.processed_title.get_tokens(keywords.AMBIGUOUS_DANCE_MUSIC) or self.manual_dance_keywords_matches or
                self.real_dance_matches
            )
        ):  # these two are implied by the above, but do it here just in case future clause re-ordering occurs
            self.dance_event = False

        elif music_or_dance_keywords >= 1 and (
            len(event_matches) + self.processed_text.count_tokens(keywords.EASY_CHOREO)
        ) >= 1 and self.calc_inverse_keyword_density < 5 and not (title_wrong_style_matches and not title_good_matches):
            self.dance_event = 'hiphop/funk and good event type'
        # one critical event and a basic dance keyword and not a wrong-dance-style and not a generic-club
        elif self.processed_text.count_tokens(keywords.EASY_DANCE) >= 1 and (
            len(event_matches) + self.processed_text.count_tokens(keywords.EASY_CHOREO)
        ) >= 1 and not self.processed_text.count_tokens(keywords.DANCE_WRONG_STYLE) and self.calc_inverse_keyword_density < 5:
            self.dance_event = 'dance event thats not a bad-style'
        elif self.processed_text.count_tokens(keywords.EASY_DANCE) >= 1 and len(
            self.found_event_matches
        ) >= 1 and not self.processed_text.count_tokens(keywords.DANCE_WRONG_STYLE) and self.processed_text.count_tokens(
            keywords.CLUB_ONLY
        ) == 0:
            self.dance_event = 'dance show thats not a club'
        elif music_or_dance_keywords >= 1 and self.processed_text.count_tokens(keywords.EASY_DANCE) >= 1:
            self.dance_event = 'good music and dance keyword'
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
    classified_event = classified_event_from_fb_event(fb_event, language)
    classified_event.classify()
    return classified_event


def relevant_keywords(event):
    text = get_relevant_text(event)
    processed_text = StringProcessor(text)
    good_keywords = processed_text.get_tokens(rules.ANY_GOOD)
    bad_keywords = processed_text.get_tokens(rules.ANY_BAD)
    return sorted(set(good_keywords).union(bad_keywords))


def highlight_keywords(text):
    import jinja2
    processed_text = StringProcessor(jinja2.Markup.escape(text))
    processed_text.replace_with(
        rules.ANY_GOOD, lambda match: jinja2.Markup('<span class="matched-text">%s</span>') % match.group(0), flags=re.I
    )
    processed_text.replace_with(rules.ANY_BAD, lambda match: jinja2.Markup('<span class="bad-matched-text">%s</span>') % match.group(0))
    return jinja2.Markup(processed_text.get_tokenized_text())


if __name__ == '__main__':
    a = [
        'club', 'bottle service', 'table service', 'coat check', 'free before', 'vip', 'guest\\W?list', 'drink specials?',
        'resident dj\\W?s?', 'dj\\W?s?', 'techno', 'trance', 'indie', 'glitch', 'bands?', 'dress to', 'mixtape', 'decks', 'r&b',
        'local dj\\W?s?', 'all night', 'lounge', 'live performances?', 'doors', 'restaurant', 'hotel', 'music shows?', 'a night of',
        'dance floor', 'beer', 'blues', 'bartenders?', 'waiters?', 'waitress(?:es)?', 'go\\Wgo', 'gogo', 'styling', 'salsa', 'bachata',
        'balboa', 'tango', 'latin', 'lindy', 'lindyhop', 'swing', 'wcs', 'samba', 'waltz', 'salsy', 'milonga', 'dance partner', 'cha cha',
        'hula', 'tumbling', 'exotic', 'cheer', 'barre', 'contact improv', 'contact improv\\w*', 'contratto mimo', 'musical theat(?:re|er)',
        'pole dance', 'flirt dance', 'bollywood', 'kalbeliya', 'bhawai', 'teratali', 'ghumar', 'indienne', 'persiana?', 'arabe', 'arabic',
        'oriental\\w*', 'oriente', 'cubana', 'capoeira', 'tahitian dancing', 'folklor\\w+', 'kizomba', 'burlesque', 'technique', 'limon',
        'clogging', 'zouk', 'afro mundo', 'class?ic[ao]', 'acroyoga', 'kirtan', 'modern dance', 'pilates', 'tribal', 'jazz', 'tap',
        'contemporary', 'contempor\\w*', 'africa\\w+', 'sabar', 'silk', 'aerial', 'zumba', 'belly\\W?danc(?:e(?:rs?)?|ing)', 'bellycraft',
        'worldbellydancealliance', 'soca', 'flamenco'
    ]
    a = sorted(a)
    print a
    print highlight_keywords(u' ๆ ซึ่งไม่ให้พี่น้อง Bboy ได้ผิดหวังอีกต่อไป*')
    print highlight_keywords('matched-text')
