# -*-*- encoding: utf-8 -*-*-

import logging
import markupsafe
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
from dancedeets.nlp import all_styles
from dancedeets.nlp import cjk_detect
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import grammar_matcher
from dancedeets.nlp import regex_keywords
from dancedeets.nlp import styles
from dancedeets.nlp.street import keywords
from dancedeets.nlp.street import rules
from dancedeets.util import dates
from dancedeets.util import language as language_util

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


class BasicClassifiedEvent(object):
    def __init__(self, fb_event, name, description, start_time, end_time, language=None, include_first_line_in_title=False):
        self.fb_event = fb_event
        self.title = name.lower()

        org_name = fb_event['info'].get('owner', {}).get('name', '').lower()

        if include_first_line_in_title:
            # Using the full first line can cause problems when it is a paragraph!
            # So let's be a bit conservative here...
            first_line = description.split('\n')[0].lower()
            if len(first_line) < 200:
                # And sometimes the org name triggers false positives, and is basically irrelevant if its just being listed in the first line
                if org_name not in first_line:
                    self.title += '\n' + first_line
        # use a separator here, so 'actors workshop' 'breaking boundaries...' doesn't match 'workshop breaking'
        self.search_text = ('\n.\n.\n.\n'.join([name, org_name, description])).lower()
        self.start_time = start_time
        self.end_time = end_time
        if not language:
            text = '%s. %s' % (fb_event['info'].get('name', ''), fb_event['info'].get('description', ''))
            language = language_util.detect_language(text)
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

        self.processed_title = grammar_matcher.StringProcessor(self.title, self.boundaries)
        self.processed_text = grammar_matcher.StringProcessor(self.search_text, self.boundaries)

        # This must be first, to remove the fake keywords
        self.processed_title.real_tokenize(keywords.PREPROCESS_REMOVAL)
        self.processed_text.real_tokenize(keywords.PREPROCESS_REMOVAL)

        global_rule = styles.PREPROCESS_REMOVAL.get(None)
        per_language_rule = styles.PREPROCESS_REMOVAL.get(self.language)
        if global_rule:
            self.processed_title.real_tokenize(global_rule)
            self.processed_text.real_tokenize(global_rule)
        if per_language_rule:
            self.processed_title.real_tokenize(per_language_rule)
            self.processed_text.real_tokenize(per_language_rule)

        # Or if there are bad keywords, lets see if we can find good keywords on a short line
        short_lines = [line for line in self.processed_text.get_tokenized_text().split('\n') if len(line) < 500]
        self.processed_short_lines = grammar_matcher.StringProcessor('\n'.join(short_lines), self.boundaries)


class ClassifiedEvent(BasicClassifiedEvent):
    def classify(self):
        super(ClassifiedEvent, self).classify()

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

        search_text = self.processed_text.get_tokenized_text()

        # Or if there are bad keywords, lets see if we can find good keywords on a short line
        short_lines = [line for line in search_text.split('\n') if len(line) < 500]
        self.processed_short_lines = grammar_matcher.StringProcessor('\n'.join(short_lines), self.boundaries)

        #if not self.processed_text.get_tokens(rules.ANY_GOOD):
        #    self.dance_event = False
        #    return
        a = time.time()
        b = time.time()
        self.manual_dance_keywords_matches = self.processed_text.get_tokens(rules.MANUAL_DANCE[grammar.STRONG])
        self.times['manual_regex'] = time.time() - b
        self.real_dance_matches = self.processed_text.get_tokens(rules.GOOD_DANCE)
        if self.processed_text.get_tokens(dance_keywords.ROMANCE):
            event_matches = self.processed_text.get_tokens(rules.EVENT_WITH_ROMANCE_EVENT)
        else:
            event_matches = self.processed_text.get_tokens(rules.EVENT)
        club_and_event_matches = self.processed_text.get_tokens(dance_keywords.PRACTICE, dance_keywords.PERFORMANCE, dance_keywords.CONTEST)
        self.times['all_regexes'] = time.time() - a

        self.found_dance_matches = self.real_dance_matches + self.processed_text.get_tokens(
            dance_keywords.EASY_DANCE, keywords.AMBIGUOUS_DANCE_MUSIC, dance_keywords.EASY_CHOREO, keywords.HOUSE, keywords.TOO_EASY_VOGUE,
            keywords.EASY_VOGUE
        ) + self.manual_dance_keywords_matches
        self.found_event_matches = event_matches + self.processed_text.get_tokens(
            keywords.EASY_EVENT, keywords.JAM
        ) + club_and_event_matches
        self.found_wrong_matches = self.processed_text.get_tokens(all_styles.DANCE_WRONG_STYLE
                                                                 ) + self.processed_text.get_tokens(keywords.CLUB_ONLY)

        title_wrong_style_matches = self.processed_title.get_tokens(all_styles.DANCE_WRONG_STYLE_TITLE)
        title_good_matches = self.processed_title.get_tokens(rules.ANY_GOOD)
        combined_matches_string = ' '.join(self.found_dance_matches + self.found_event_matches)
        dummy, combined_matches = re.subn(r'\w+', '', combined_matches_string)
        dummy, words = re.subn(r'\w+', '', re.sub(r'\bhttp.*?\s', '', search_text))
        fraction_matched = 1.0 * (combined_matches + 1) / (words + 1)
        if not fraction_matched:
            self.calc_inverse_keyword_density = 100
        else:
            self.calc_inverse_keyword_density = -math.log(fraction_matched, 2)

        #print self.processed_text.count_tokens(dance_keywords.EASY_DANCE)
        #print len(club_and_event_matches)
        #print self.processed_text.count_tokens(all_styles.DANCE_WRONG_STYLE)
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
            len(event_matches) + self.processed_text.count_tokens(dance_keywords.EASY_CHOREO)
        ) >= 1 and self.calc_inverse_keyword_density < 5 and not (title_wrong_style_matches and not title_good_matches):
            self.dance_event = 'hiphop/funk and good event type'
        # one critical event and a basic dance keyword and not a wrong-dance-style and not a generic-club
        elif self.processed_text.count_tokens(dance_keywords.EASY_DANCE) >= 1 and (
            len(event_matches) + self.processed_text.count_tokens(dance_keywords.EASY_CHOREO)
        ) >= 1 and not self.processed_text.count_tokens(all_styles.DANCE_WRONG_STYLE) and self.calc_inverse_keyword_density < 5:
            self.dance_event = 'dance event thats not a bad-style'
        elif self.processed_text.count_tokens(dance_keywords.EASY_DANCE) >= 1 and len(
            self.found_event_matches
        ) >= 1 and not self.processed_text.count_tokens(all_styles.DANCE_WRONG_STYLE) and self.processed_text.count_tokens(
            keywords.CLUB_ONLY
        ) == 0:
            self.dance_event = 'dance show thats not a club'
        elif music_or_dance_keywords >= 1 and self.processed_text.count_tokens(dance_keywords.EASY_DANCE) >= 1:
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


def get_classified_event(fb_event, language=None, classifier_type=ClassifiedEvent):
    classified_event = classifier_type(
        fb_event,
        fb_event['info'].get('name', ''),
        fb_event['info'].get('description', ''),
        dates.parse_fb_start_time(fb_event),
        dates.parse_fb_end_time(fb_event),
        language=language,
        include_first_line_in_title=True
    )
    classified_event.classify()
    return classified_event


def relevant_keywords(event):
    text = get_relevant_text(event)
    processed_text = grammar_matcher.StringProcessor(text)
    good_keywords = processed_text.get_tokens(rules.ANY_GOOD)
    return sorted(set(good_keywords))


def highlight_keywords(text):
    import markupsafe
    processed_text = grammar_matcher.StringProcessor(markupsafe.Markup.escape(text))
    processed_text.replace_with(
        rules.ANY_GOOD, lambda match: markupsafe.Markup('<span class="matched-text">%s</span>') % match.group(0), flags=re.I
    )
    return markupsafe.Markup(processed_text.get_tokenized_text())


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
    print(a)
    print(highlight_keywords(u' ๆ ซึ่งไม่ให้พี่น้อง Bboy ได้ผิดหวังอีกต่อไป*'))
    print(highlight_keywords('matched-text'))
