import datetime
import logging
import re
from dancedeets import event_types
from . import event_classifier
from . import event_structure
from . import grammar
from .street import keywords
from .street import rules
Any = grammar.Any
Name = grammar.Name
commutative_connected = grammar.commutative_connected


def log_to_bucket(category):
    def wrap_func(func):
        def outer_func(self, *args, **kwargs):
            self._log_category = category
            try:
                result = func(self, *args, **kwargs)
                self._log('Final result: %s', result)
                return result
            finally:
                self._log_category = None

        return outer_func

    return wrap_func


NEVER_TOKEN = Any('_NEVER_FOUND_TOKEN_WINVO:INDLKESP_')

style_keywords = {
    event_types.VERTICALS.STREET: rules.STREET_STYLES,
    event_types.VERTICALS.LATIN: keywords.DANCE_STYLE_LATIN,
    event_types.VERTICALS.SWING: keywords.DANCE_STYLE_SWING,
    event_types.VERTICALS.TANGO: keywords.DANCE_STYLE_TANGO,
    event_types.VERTICALS.CAPOEIRA: keywords.DANCE_STYLE_CAPOEIRA,
    event_types.VERTICALS.BALLROOM: keywords.DANCE_STYLE_BALLROOM,
    event_types.VERTICALS.ZOUK: keywords.DANCE_STYLE_ZOUK,
    event_types.VERTICALS.WCS: keywords.DANCE_STYLE_WCS,
    event_types.VERTICALS.PARTNER_FUSION: keywords.NO_MATCH,
}

misc_keyword_sets = [
    keywords.DANCE_STYLE_CLASSICAL,
    keywords.DANCE_STYLE_AFRICAN,
    keywords.DANCE_STYLE_INDIAN,
    keywords.DANCE_STYLE_SEXY,
    keywords.DANCE_STYLE_MISC,
]


def all_styles_except(vertical):
    keyword_sets = set(style_keywords.values())
    keyword_sets.update(misc_keyword_sets)
    if vertical:
        keyword_sets.remove(style_keywords[vertical])
    return Any(*keyword_sets)


ALL_STYLES = all_styles_except(None)


class RuleGenerator(type):
    def __init__(cls, name, parents, attr):
        super(RuleGenerator, cls).__init__(name, parents, attr)
        if parents == (object,):
            # Skip all this logic if we're building DanceStyleEventClassifier.
            # Only run these for the subclasses of DanceStyleEventClassifier.
            return
        #TODO: setup BAD_DANCE keywords set up across the board...
        cls.GOOD_DANCE = Name('GOOD_DANCE', cls.GOOD_DANCE or keywords.NO_MATCH)
        cls.AMBIGUOUS_DANCE = Name('AMBIGUOUS_DANCE', cls.AMBIGUOUS_DANCE or keywords.NO_MATCH)
        cls.BAD_DANCE = Name('BAD_DANCE', cls.BAD_DANCE or keywords.NO_MATCH)
        cls.ADDITIONAL_EVENT_TYPE = cls.ADDITIONAL_EVENT_TYPE or keywords.NO_MATCH

        cls.NOT_DANCE = Any(
            keywords.WRONG_BATTLE_STYLE,
            keywords.WRONG_AUDITION,
        )

        cls.BAD_DANCE_FULL = Any(
            cls.BAD_DANCE,
            cls.NOT_DANCE,
            all_styles_except(cls.vertical),
        )

        UNAMBIGUOUS_DANCE = commutative_connected(cls.AMBIGUOUS_DANCE, keywords.EASY_DANCE)
        cls.GOOD_DANCE_FULL = Any(UNAMBIGUOUS_DANCE, cls.GOOD_DANCE)
        cls.GOOD_OR_AMBIGUOUS_DANCE = Name('GOOD_OR_AMBIGUOUS_DANCE', Any(cls.AMBIGUOUS_DANCE, UNAMBIGUOUS_DANCE, cls.GOOD_DANCE))
        cls.COMPETITIONS = Any(
            keywords.BATTLE,
            keywords.CONTEST,
            keywords.JAM,
        )
        cls.EVENT_TYPE = Any(
            keywords.CLASS,
            keywords.AUDITION,
            keywords.PERFORMANCE,
            keywords.PRACTICE,
            keywords.EASY_CLUB,
            cls.COMPETITIONS,
            cls.ADDITIONAL_EVENT_TYPE,
        )
        cls.EVENT_TYPE_ROMANCE = Any(cls.EVENT_TYPE, keywords.ROMANCE_LANGUAGE_CLASS)
        cls.GOOD_DANCE_COMPETITION = Name(
            'GOOD_DANCE_COMPETITION', commutative_connected(Any(cls.GOOD_DANCE_FULL, cls.AMBIGUOUS_DANCE), cls.COMPETITIONS)
        )
        cls.GOOD_DANCE_EVENT = Name(
            'GOOD_DANCE_EVENT',
            Any(
                commutative_connected(cls.GOOD_DANCE_FULL, cls.EVENT_TYPE),
                commutative_connected(cls.AMBIGUOUS_DANCE, keywords.CLASS),
            )
        )
        cls.GOOD_DANCE_EVENT_ROMANCE = Name(
            'GOOD_DANCE_EVENT_ROMANCE',
            Any(
                commutative_connected(cls.GOOD_DANCE_FULL, cls.EVENT_TYPE_ROMANCE),
                commutative_connected(cls.AMBIGUOUS_DANCE, Any(keywords.CLASS, keywords.ROMANCE_LANGUAGE_CLASS)),
            )
        )
        cls.BAD_DANCE_EVENT = Name('BAD_DANCE_EVENT', commutative_connected(cls.BAD_DANCE_FULL, cls.EVENT_TYPE))
        cls.BAD_DANCE_EVENT_ROMANCE = Name('GOOD_DANCE_EVENT_ROMANCE', commutative_connected(cls.BAD_DANCE_FULL, cls.EVENT_TYPE_ROMANCE))


class DanceStyleEventClassifier(object):
    __metaclass__ = RuleGenerator

    # mostly used for logging, for now...
    vertical = None

    # rules and keywords
    AMBIGUOUS_DANCE = None
    GOOD_DANCE = None
    BAD_DANCE = None
    ADDITIONAL_EVENT_TYPE = None
    GOOD_BAD_PAIRINGS = []

    def __init__(self, classified_event, debug=True):
        if not self.vertical:
            raise ValueError('Need to configure vertical')

        self._classified_event = classified_event
        self._debug = debug

        self._logs = []
        self._log_category = None

    # utility methods
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
        if not self._debug:
            return
        self._logs.append('%s: %s' % (self._log_category, log % args))

    # top-level function
    def is_dance_event(self):
        if not self._quick_is_dance_event():
            self._log('not a sufficiently dancey event')
            return False

        if self._has_wrong_meaning_for_style():
            self._log('wrong meaning for style')
            return False

        # Handles all audition cases
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

    @log_to_bucket('organizer')
    def has_strong_organizer(self):
        org_name = self._classified_event.fb_event['info'].get('owner', {}).get('name', '').lower()
        sp = event_classifier.StringProcessor(org_name)
        has_dance_organizer = sp.has_token(self.GOOD_DANCE_FULL)
        self._log('Searching organizer (%s) for %s, has: %s', org_name, self.GOOD_DANCE_FULL.name(), has_dance_organizer)
        if has_dance_organizer:
            self._log('Has good dance in event organizer: %s' % has_dance_organizer)
            return 'Has good dance in event organizer'
        return False

    @log_to_bucket('strong_title')
    def has_strong_title(self):
        # Some super-basic language specialization
        if self._has(keywords.ROMANCE):
            event_type = self.EVENT_TYPE_ROMANCE
            good_dance_event = self.GOOD_DANCE_EVENT_ROMANCE
        else:
            event_type = self.EVENT_TYPE
            good_dance_event = self.GOOD_DANCE_EVENT

        is_dance_ish = len(set(self._get(self.GOOD_OR_AMBIGUOUS_DANCE) + self._get(keywords.EASY_DANCE))) >= 2
        self._log('is_dance_ish: %s', is_dance_ish)

        # Has 'popping' and actually seems related-to-dance-as-a-whole
        if self._title_has(self.GOOD_DANCE_FULL) and is_dance_ish:
            return 'title has good_dance, and is dance-y event'

        # Has 'popping with' and has some class-y stuff in the body
        if self._title_has(self.GOOD_DANCE_FULL) and self._title_has(keywords.WITH) and len(set(self._get(keywords.CLASS))) >= 2:
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
        if self._title_has(event_type) and self._has(self.GOOD_DANCE_FULL) and not self._has(self.BAD_DANCE_FULL):
            return 'title has event_type, body had good and not bad keywords'

        return False

    @log_to_bucket('strong_body')
    def has_strong_body(self):
        # Some super-basic language specialization
        if self._has(keywords.ROMANCE):
            good_dance_event = self.GOOD_DANCE_EVENT_ROMANCE
        else:
            good_dance_event = self.GOOD_DANCE_EVENT

        if self._has(good_dance_event) and not self._has(self.BAD_DANCE_FULL):
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

        has_bad_keywords = self._short_lines_have(self.BAD_DANCE_FULL)
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
        if self._title_has(self.BAD_DANCE_FULL):
            return False

        # if title is good strong keyword, and we have a list of classes:
        # why doesn't this get found by the is_workshop title classifier? where is our 'camp' keyword
        # https://www.dancedeets.com/events/admin_edit?event_id=317006008387038

        schedule_groups = event_structure.get_schedule_line_groups(self._classified_event)
        for schedule_lines in schedule_groups:
            good_lines = []
            for line in schedule_lines:
                proc_line = event_classifier.StringProcessor(line, self._classified_event.boundaries)
                good_matches = proc_line.get_tokens(self.GOOD_OR_AMBIGUOUS_DANCE)
                has_bad_matches = proc_line.has_token(self.BAD_DANCE_FULL)

                # Sometimes we have a schedule with hiphop and ballet
                # Sometimes we have a schedule with hiphop and dj and beatbox/rap (more on music side)
                # Sometimes we have a schedule with hiphop, house, and beatbox (legit, crosses boundaries)
                # TODO: Should do a better job of classifying the ambiguous music/dance types, based on the presence of non-ambiguous dance types too
                if good_matches and not has_bad_matches:
                    self._log('Found %s in line', good_matches)
                    good_lines.append(good_matches)
            # If more than 10% are good, then we found a good class
            self._log('Found %s of %s events with good styles', len(good_lines), len(schedule_lines))
            if len(good_lines) > len(schedule_lines) / 10:
                return 'found schedule list with good styles'
        return False


class StreetClassifier(DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.STREET

    AMBIGUOUS_DANCE = keywords.AMBIGUOUS_DANCE_MUSIC
    GOOD_DANCE = Any(rules.good_dance, rules.MANUAL_DANCER[grammar.STRONG_WEAK])
    GOOD_BAD_PAIRINGS = [
        (keywords.STYLE_HOUSE, keywords.WRONG_HOUSE),
        (keywords.STYLE_BREAK, keywords.WRONG_BREAK),
        (keywords.STYLE_LOCK, keywords.WRONG_LOCK),
        (keywords.STYLE_FLEX, keywords.WRONG_FLEX),
        (keywords.STYLE_FLEX, keywords.WRONG_FLEX),
    ]
    BAD_DANCE = Any(
        keywords.DANCE_WRONG_STYLE,
        keywords.DANCE_WRONG_STYLE_TITLE_ONLY,
        keywords.WRONG_BATTLE_STYLE,
        keywords.WRONG_AUDITION,
    )
