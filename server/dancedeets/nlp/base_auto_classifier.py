import datetime
import logging
import re
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import event_structure
from dancedeets.nlp import grammar
from dancedeets.nlp import grammar_matcher
from .street import keywords
from .street import rules
from dancedeets.util import runtime
Any = grammar.Any
Name = grammar.Name
commutative_connected = grammar.commutative_connected


def log_to_bucket(category):
    def wrap_func(func):
        def outer_func(self, *args, **kwargs):
            self._log_category.append(category)
            try:
                result = func(self, *args, **kwargs)
                self._log('Final result: %s', result)
                return result
            finally:
                self._log_category.pop()

        return outer_func

    return wrap_func


NEVER_TOKEN = Any('_NEVER_FOUND_TOKEN_WINVO:INDLKESP_')


class RuleGenerator(type):
    def __init__(cls, name, parents, attr):
        super(RuleGenerator, cls).__init__(name, parents, attr)
        if parents == (object,):
            # Skip all this logic if we're building DanceStyleEventClassifier.
            # Only run these for the subclasses of DanceStyleEventClassifier.
            return
        cls.SUPER_STRONG_KEYWORDS = Name('SUPER_STRONG_KEYWORDS', cls.SUPER_STRONG_KEYWORDS or keywords.NO_MATCH)
        cls.GOOD_DANCE = Name('GOOD_DANCE', cls.GOOD_DANCE or keywords.NO_MATCH)
        cls.AMBIGUOUS_DANCE = Name('AMBIGUOUS_DANCE', cls.AMBIGUOUS_DANCE or keywords.NO_MATCH)
        cls.OTHER_DANCE = Name('OTHER_DANCE', cls.OTHER_DANCE or keywords.NO_MATCH)
        cls.ADDITIONAL_EVENT_TYPE = cls.ADDITIONAL_EVENT_TYPE or keywords.NO_MATCH
        cls.DANCE_KEYWORDS = cls.DANCE_KEYWORDS or keywords.NO_MATCH

        UNAMBIGUOUS_DANCE = commutative_connected(cls.AMBIGUOUS_DANCE, Any(dance_keywords.EASY_DANCE, dance_keywords.EASY_CHOREO))
        cls.GOOD_DANCE_FULL = Name('GOOD_DANCE_FULL', Any(UNAMBIGUOUS_DANCE, cls.GOOD_DANCE))
        cls.GOOD_OR_AMBIGUOUS_DANCE = Name('GOOD_OR_AMBIGUOUS_DANCE', Any(cls.AMBIGUOUS_DANCE, UNAMBIGUOUS_DANCE, cls.GOOD_DANCE))
        cls.COMPETITIONS = Any(
            dance_keywords.BATTLE,
            dance_keywords.CONTEST,
            keywords.JAM,
        )
        cls.EVENT_TYPE = Any(
            dance_keywords.CLASS,
            dance_keywords.AUDITION,
            dance_keywords.PERFORMANCE,
            dance_keywords.PRACTICE,
            keywords.EASY_CLUB,
            cls.COMPETITIONS,
            cls.ADDITIONAL_EVENT_TYPE,
        )
        cls.EVENT_TYPE_ROMANCE = Any(cls.EVENT_TYPE, dance_keywords.ROMANCE_LANGUAGE_CLASS)
        cls.EVENT_TYPE_SPANISH = Any(cls.EVENT_TYPE, dance_keywords.SPANISH_CLASS)
        cls.GOOD_DANCE_COMPETITION = Name(
            'GOOD_DANCE_COMPETITION', commutative_connected(Any(cls.GOOD_DANCE_FULL, cls.AMBIGUOUS_DANCE), cls.COMPETITIONS)
        )
        cls.GOOD_DANCE_EVENT = Name(
            'GOOD_DANCE_EVENT',
            Any(
                commutative_connected(cls.GOOD_DANCE_FULL, cls.EVENT_TYPE),
                commutative_connected(cls.AMBIGUOUS_DANCE, dance_keywords.CLASS),
            )
        )
        cls.GOOD_DANCE_EVENT_ROMANCE = Name(
            'GOOD_DANCE_EVENT_ROMANCE',
            Any(
                commutative_connected(cls.GOOD_DANCE_FULL, cls.EVENT_TYPE_ROMANCE),
                commutative_connected(cls.AMBIGUOUS_DANCE, Any(dance_keywords.CLASS, dance_keywords.ROMANCE_LANGUAGE_CLASS)),
            )
        )
        cls.GOOD_DANCE_EVENT_SPANISH = Name(
            'GOOD_DANCE_EVENT_SPANISH',
            Any(
                commutative_connected(cls.GOOD_DANCE_FULL, cls.EVENT_TYPE_SPANISH),
                commutative_connected(cls.AMBIGUOUS_DANCE, Any(dance_keywords.CLASS, dance_keywords.SPANISH_CLASS)),
            )
        )


class DanceStyleEventClassifier(object):
    __metaclass__ = RuleGenerator

    # mostly used for logging, for now...
    vertical = None

    # rules and keywords
    AMBIGUOUS_DANCE = None
    GOOD_DANCE = None
    SUPER_STRONG_KEYWORDS = None
    OTHER_DANCE = None
    ADDITIONAL_EVENT_TYPE = None
    DANCE_KEYWORDS = None
    GOOD_BAD_PAIRINGS = []

    def __init__(self, classified_event, debug=None):
        if not self.vertical:
            raise ValueError('Need to configure vertical')

        self._classified_event = classified_event
        if debug is None:
            debug = runtime.is_local_appengine()
        self._debug = debug

        self._logs = []
        self._log_category = ['global']
        self._log('Detected language %s', self._classified_event.language)

    @classmethod
    def finalize_class(cls, other_style_regexes):
        cls.OTHER_REGEXES = [
            cls.OTHER_DANCE,
            keywords.WRONG_BATTLE_STYLE,
            keywords.WRONG_AUDITION,
            keywords.OTHER_SHOW,
        ] + list(other_style_regexes)

        # make this function a no-op the next time it's called
        @classmethod
        def dummy_finalize_class(*args):
            pass

        cls.finalize_class = dummy_finalize_class

    # utility methods
    def _title_has_other(self):
        for x in self.OTHER_REGEXES:
            result = self._title_has(x)
            if result:
                return result
        return None

    def _has_other(self):
        for x in self.OTHER_REGEXES:
            result = self._has(x)
            if result:
                return result
        return None

    def _short_lines_have_other(self):
        for x in self.OTHER_REGEXES:
            result = self._short_lines_have(x)
            if result:
                return result
        return None

    def _title_get(self, keyword):
        result = self._classified_event.processed_title.get_tokens(keyword)
        self._log('Searching title for %s, got: %s', keyword.name(), result)
        return result

    def _short_lines_get(self, keyword):
        result = self._classified_event.processed_short_lines.get_tokens(keyword)
        self._log('Searching short lines for %s, got: %s', keyword.name(), result)
        return result

    def _get(self, keyword):
        result = self._classified_event.processed_text.get_tokens(keyword)
        self._log('Searching text for %s, got: %s', keyword.name(), result)
        return result

    def _title_has(self, keyword):
        result = self._classified_event.processed_title.has_token(keyword)
        self._log('Searching title for %s, have: %s', keyword.name(), result)
        return result

    def _short_lines_have(self, keyword):
        result = self._classified_event.processed_short_lines.has_token(keyword)
        self._log('Searching short lines for %s, have: %s', keyword.name(), result)
        return result

    def _has(self, keyword):
        result = self._classified_event.processed_text.has_token(keyword)
        self._log('Searching text for %s, have: %s', keyword.name(), result)
        return result

    def _log(self, log, *args):
        self._logs.append('%s: %s' % (self._log_category[-1], log % args))
        if not self._debug:
            return
        logging.info('%s: %s', self._log_category[-1], log % args)

    # top-level function
    def is_dance_event(self):
        self._log('Starting %s classifier', self.vertical)

        if not self._quick_is_dance_event():
            self._log('not a sufficiently dancey event')
            return False

        if self._has_wrong_meaning_for_style():
            self._log('wrong meaning for style')
            return False

        result = self.has_super_strong()
        if result: return result

        result = self.has_strong_title()
        if result: return result

        result = self.is_competition()
        if result: return result

        # generally catches practice or performances
        result = self.has_strong_body()
        if result: return result

        # generally catches practice or performances
        result = self.has_strong_organizer()
        if result: return result

        # has a list of scheduled timeslots with some good styles in it
        result = self.has_list_of_good_classes()
        if result: return result

        return False

    def debug_info(self):
        return self._logs

    def _quick_is_dance_event(self):
        raise NotImplementedError()

    def _has_wrong_meaning_for_style(self):
        for good, bad in self.GOOD_BAD_PAIRINGS:
            if self._has(good) and self._has(bad):
                return True
        return False

    @log_to_bucket('super_strong')
    def has_super_strong(self):
        if self._title_has(self.SUPER_STRONG_KEYWORDS):
            return 'title has super-strong keyword'

        if self._has(self.SUPER_STRONG_KEYWORDS) and self._get(dance_keywords.EASY_DANCE):
            return 'body has super-strong keyword and seems dance-y'

        return False

    @log_to_bucket('organizer')
    def has_strong_organizer(self):
        title_is_other_dance = self._title_has_other()
        if title_is_other_dance:
            return False

        org_name = self._classified_event.fb_event['info'].get('owner', {}).get('name', '').lower()
        sp = grammar_matcher.StringProcessor(org_name)

        has_dance_organizer = sp.has_token(self.GOOD_DANCE_FULL)
        self._log('Searching organizer (%s) for %s, has: %s', org_name, self.GOOD_DANCE_FULL.name(), has_dance_organizer)
        if has_dance_organizer:
            self._log('Has good dance in event organizer: %s' % has_dance_organizer)
            return 'Has good dance in event organizer'

        has_super_strong_dance_organizer = sp.has_token(self.SUPER_STRONG_KEYWORDS)
        self._log('Searching organizer (%s) for %s, has: %s', org_name, self.SUPER_STRONG_KEYWORDS.name(), has_dance_organizer)
        if has_super_strong_dance_organizer:
            self._log('Has super-strong dance in event organizer: %s' % has_dance_organizer)
            return 'Has super-strong dance in event organizer'
        return False

    @log_to_bucket('dance_ish')
    def is_dance_ish(self):
        keywords = set()
        for x in [
            self._get(self.GOOD_OR_AMBIGUOUS_DANCE),
            self._get(dance_keywords.EASY_DANCE),
            self._get(dance_keywords.EASY_CHOREO),
            self._get(self.DANCE_KEYWORDS),
        ]:
            keywords.update(x)
        is_dance_ish = len(keywords) >= 2
        self._log('is_dance_ish: %s with keywords: %s', is_dance_ish, keywords)
        return is_dance_ish

    @log_to_bucket('strong_title')
    def has_strong_title(self):
        # Some super-basic language specialization
        if self._classified_event.language in ['es', 'pt']:
            event_type = self.EVENT_TYPE_SPANISH
            good_dance_event = self.GOOD_DANCE_EVENT_SPANISH
        elif self._classified_event.language in ['fr', 'it']:
            event_type = self.EVENT_TYPE_ROMANCE
            good_dance_event = self.GOOD_DANCE_EVENT_ROMANCE
        else:
            event_type = self.EVENT_TYPE
            good_dance_event = self.GOOD_DANCE_EVENT

        is_dance_ish = self.is_dance_ish()

        # Has 'popping' and actually seems related-to-dance-as-a-whole
        if self._title_has(self.GOOD_DANCE_FULL) and is_dance_ish:
            return 'title has good_dance, and is dance-y event'

        # Has 'popping with' and has some class-y stuff in the body
        if self._title_has(self.GOOD_DANCE_FULL) and self._title_has(dance_keywords.WITH
                                                                    ) and len(set(self._get(dance_keywords.CLASS))) >= 2:
            return 'title has good_dance, and is dance-y event'

        # Has 'hiphop dance workshop/battle/audition'
        if self._title_has(good_dance_event):
            return 'title has good_dance-event_type'

        # Has 'workshop' and ('hiphop' or 'tango') and seems dance-y
        # If the title contains a good keyword, and the body contains a bad keyword, this one will trigger (but the one below will not)
        if self._title_has(event_type) and self._title_has(self.GOOD_OR_AMBIGUOUS_DANCE) and is_dance_ish:
            return 'title has event_type and ambiguous-or-good dance word, and is dance-y event'

        # Has 'workshop' and ('hiphop dance' or 'moptop') and not 'modern'
        # If the title contains a good keyword, and the body contains a bad keyword, this one will trigger (but the one below will not)
        if self._title_has(event_type) and self._title_has(self.GOOD_DANCE_FULL):
            return 'title has event_type, good keywords'

        # Has 'workshop' and body has ('hiphop dance' but not 'ballet')
        if self._title_has(event_type) and self._has(self.GOOD_DANCE_FULL) and not self._has_other():
            return 'title has event_type, body had good and not bad keywords'

        return False

    @log_to_bucket('strong_body')
    def has_strong_body(self):
        # Some super-basic language specialization
        if self._classified_event.language in ['es', 'pt']:
            good_dance_event = self.GOOD_DANCE_EVENT_SPANISH
        elif self._classified_event.language in ['fr', 'it']:
            good_dance_event = self.GOOD_DANCE_EVENT_ROMANCE
        else:
            good_dance_event = self.GOOD_DANCE_EVENT

        if self._has(good_dance_event) and not self._title_has_other():
            return 'body has good dance event, and title does not have bad keywords'

        if self._short_lines_have(good_dance_event):
            return 'body has short line containing good dance event'

        # have some strong keywords on lines by themselves
        solo_lines_regex = self.GOOD_DANCE_FULL.hack_double_regex()[self._classified_event.boundaries]
        good_matches = set()
        for line in self._classified_event.search_text.split('\n'):
            alpha_line = re.sub(r'\W+', '', line)
            if not alpha_line:
                continue
            remaining_line = solo_lines_regex.sub('', line)
            deleted_length = len(line) - len(remaining_line)
            if 0.5 < 1.0 * deleted_length / len(alpha_line):
                good_matches.add(solo_lines_regex.findall(line)[0])  # at most one keyword per line
        if len(good_matches) >= 2:
            return 'found good keywords on lines by themselves: %s' % set(good_matches)

        return False

    @log_to_bucket('competition')
    def is_competition(self):
        has_competition = self._short_lines_have(self.GOOD_DANCE_COMPETITION)

        has_bad_keywords = self._short_lines_have_other()
        if has_competition and not has_bad_keywords:
            return 'is good-dance battle event, with no bad keywords'

        has_competitors = event_structure.find_competitor_list(self._classified_event.search_text)
        has_start_judge = self._has(rules.START_JUDGE)
        is_battle_event = (has_start_judge or has_competitors)

        if is_battle_event and len(self._short_lines_get(self.GOOD_DANCE_FULL)) >= 2 and not has_bad_keywords:
            return 'is battle event, with a few good keywords, and no bad keywords'

        return False

    @log_to_bucket('list_of_good_classes')
    def has_list_of_good_classes(self):
        # A "list of times with dance/music things" can often be clubs as well as classes

        # So let's try to throw out club-things first
        start_time = self._classified_event.start_time
        end_time = self._classified_event.end_time
        # Ignore club events (ends in the morning and less than 12 hours long)
        if end_time and end_time.time() < datetime.time(12) and end_time - start_time < datetime.timedelta(hours=12):
            return False

        if len(set(self._get(keywords.CLUB_ONLY))) > 2:
            return False
        #if self._title_has_other():
        #    return False

        # if title is good strong keyword, and we have a list of classes:
        # why doesn't this get found by the is_workshop title classifier? where is our 'camp' keyword
        # https://www.dancedeets.com/events/admin_edit?event_id=317006008387038

        schedule_groups = event_structure.get_schedule_line_groups(self._classified_event)
        for schedule_lines in schedule_groups:
            good_lines = []
            bad_lines = []
            for line in schedule_lines:
                proc_line = grammar_matcher.StringProcessor(line, self._classified_event.boundaries)
                good_matches = proc_line.get_tokens(self.GOOD_OR_AMBIGUOUS_DANCE)

                bad_matches = set()
                for x in self.OTHER_REGEXES:
                    bad_matches.update(proc_line.get_tokens(x))

                # Sometimes we have a schedule with hiphop and ballet
                # Sometimes we have a schedule with hiphop and dj and beatbox/rap (more on music side)
                # Sometimes we have a schedule with hiphop, house, and beatbox (legit, crosses boundaries)
                # TODO: Should do a better job of classifying the ambiguous music/dance types, based on the presence of non-ambiguous dance types too
                if good_matches and not bad_matches:
                    self._log('Found %s in line', good_matches)
                    good_lines.append(good_matches)
                if not good_matches and bad_matches:
                    bad_lines.append(bad_matches)
            num_dance_lines = len(good_lines) + len(bad_lines)
            self._log('Found %s of %s lines with dance styles', num_dance_lines, len(schedule_lines))
            # If more than 10% are good, then we found a good class
            self._log('Found %s of %s lines with good styles', len(good_lines), len(schedule_lines))
            if len(good_lines) > len(schedule_lines) / 10 and num_dance_lines >= 2:
                return 'found schedule list with good styles'
        return False
