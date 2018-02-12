from . import event_classifier
from . import grammar
from street import keywords
from street import rules
Any = grammar.Any
Name = grammar.Name
commutative_connected = grammar.commutative_connected


def _log_to_bucket(category):
    def wrap_func(func):
        def outer_func(self, *args, **kwargs):
            self._log_category = category
            try:
                result = func(self, *args, **kwargs)
                self._log('Final result: %s', result)
            finally:
                self._log_category = None

        return outer_func

    return wrap_func


STRONG_EVENT = Name(
    'PERFORMANCE_PRACTICE', commutative_connected(rules.GOOD_DANCE, Any(
        keywords.PERFORMANCE,
        keywords.PRACTICE,
        keywords.BATTLE,
    ))
)


class DanceStyleEventClassifier(object):
    vertical = None

    def __init__(self, classified_event, debug=True):
        self._classified_event = classified_event
        self._debug = debug

        self._logs = {}
        self._log_category = None

        if not self.vertical:
            raise ValueError('Need to configure vertical')

    # utility methods
    def _title_has(self, keyword):
        result = self._classified_event.processed_title.has_token(keyword)
        self._log('Searching title for %s, found: %s', keyword.name(), result)
        return result

    def _has(self, keyword):
        result = self._classified_event.processed_text.has_token(keyword)
        self._log('Searching text for %s, found: %s', keyword.name(), result)
        return result

    def _log(self, log, *args):
        if not self._debug:
            return
        if self._log_category not in self._logs:
            self._logs[self._log_category] = []
        self._logs[self._log_category].append(log % args)

    # top-level function
    def is_dance_event(self):
        result = self.is_audition()
        if result: return result

        result = self.is_workshop()
        if result: return result

        # generally catches practice or performances
        result = self.has_strong_event_on_short_line()
        if result: return result

        return False

    def _quick_is_dance_event(self):
        raise NotImplementedError()

    def _has_wrong_meaning_for_style(self):
        good_bad_pairings = [
            (keywords.STYLE_HOUSE, keywords.WRONG_HOUSE),
            (keywords.STYLE_BREAK, keywords.WRONG_BREAK),
            (keywords.STYLE_LOCK, keywords.WRONG_LOCK),
            (keywords.STYLE_FLEX, keywords.WRONG_FLEX),
        ]
        for good, bad in good_bad_pairings:
            if self._has(good) and self._has(bad):
                return True
        return False

    @_log_to_bucket('audition')
    def is_audition(self):
        if not self._quick_is_dance_event():
            self._log('not a sufficiently dancey event')
            return False

        # first check for audition in title
        has_audition = self._title_has(keywords.AUDITION)
        if not has_audition:
            return False

        # now check for good keywords in title
        has_good_dance_title = self._title_has(rules.GOOD_DANCE)
        has_extended_good_crew_title = self._title_has(rules.MANUAL_DANCER[grammar.STRONG_WEAK])
        if has_good_dance_title or has_extended_good_crew_title:
            return "audition title and good keywords"

        # now check the body for good stuff and no bad stuff
        has_good_dance = self._has(rules.GOOD_DANCE)
        if not has_good_dance:
            return False

        has_wrong_style = self._has(rules.DANCE_WRONG_STYLE_TITLE)
        has_wrong_audition = self._has(keywords.WRONG_AUDITION)
        if has_wrong_style or has_wrong_audition:
            return False

        return "audition title and body has good and not bad keywords"

    @_log_to_bucket('workshop')
    def is_workshop(self):
        if self._has_wrong_meaning_for_style(self):
            return False

        # Has "hiphop dance workshop"
        has_good_dance_class_title = self._title_has(rules.GOOD_DANCE_CLASS)
        if has_good_dance_class_title:
            return "title has good dance workshop"

        # Has "workshop" and ("hiphop dance" or "moptop") and not "modern"
        #TODO: solve the problem of "modern hiphop dance workshop" or "hiphop dance at my ballet studio" titles again.
        # Some super-basic language specialization
        if self._has(keywords.ROMANCE):
            has_class_title = self._title_has(rules.ROMANCE_EXTENDED_CLASS)
        else:
            has_class_title = self._title_has(keywords.CLASS)
        has_good_dance_title = self._title_has(rules.GOOD_DANCE)
        has_extended_good_crew_title = self._title_has(rules.MANUAL_DANCER[grammar.STRONG_WEAK])
        has_wrong_style_title = self._title_has(rules.DANCE_WRONG_STYLE_TITLE)
        if has_class_title and (has_good_dance_title or has_extended_good_crew_title) and not has_wrong_style_title:
            return "title has workshop, good and not bad keywords"

        # Has "workshop" and body has ("hiphop dance" but not "ballet")
        has_wrong_style = self._has(rules.DANCE_WRONG_STYLE_TITLE)
        has_good_dance = self._has(rules.GOOD_DANCE)
        has_good_crew = self._has(rules.MANUAL_DANCER[grammar.STRONG])
        if has_class_title and not has_wrong_style and (has_good_dance or has_good_crew):
            return "title has workshop, body had good and not bad keywords"

        # Body has "workshop" and title doesn't disqualify it ("modern dance workshop")
        has_good_dance_class = self._has(rules.GOOD_DANCE_CLASS)
        if has_good_dance_class and not has_wrong_style_title:
            return "body has good dance workshop, and title does not have bad keywords"

        return False

    @_log_to_bucket('strong_event_on_short_line')
    def has_strong_event_on_short_line(self):
        text = self._classified_event.processed_text.get_tokenized_text()

        for line in text.split('\n'):
            pline = event_classifier.StringProcessor(line, self._classified_event.boundaries)
            # Skip the long bios with crap in them
            if len(line) > 500:
                continue
            pp = pline.has_token(STRONG_EVENT)
            if pp:
                self._log('found strong event (%s) on short line: %s', pp, pline)
                return True
        return False

    def has_list_of_good_classes(self):
        pass

    def has_many_street_styles(self):
        pass

    def has_standalone_keywords(self):
        pass
