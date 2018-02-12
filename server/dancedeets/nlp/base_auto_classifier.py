from . import event_classifier
from . import event_structure
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


GOOD_DANCE = Any(rules.good_dance, rules.MANUAL_DANCER[grammar.STRONG_WEAK])
EVENT_TYPE = Any(
    keywords.CLASS,
    keywords.AUDITION,
    keywords.PERFORMANCE,
    keywords.PRACTICE,
    keywords.BATTLE,
)
EVENT_TYPE_ROMANCE = Any(EVENT_TYPE, keywords.ROMANCE_EXTENDED_CLASS)
GOOD_DANCE_EVENT = commutative_connected(rules.good_dance, EVENT_TYPE)
GOOD_DANCE_EVENT_ROMANCE = commutative_connected(rules.good_dance, EVENT_TYPE_ROMANCE)
BAD_DANCE_KEYWORDS = Any(
    keywords.DANCE_WRONG_STYLE,
    keywords.DANCE_WRONG_STYLE_TITLE_ONLY,
    keywords.WRONG_BATTLE_STYLE,
    keywords.WRONG_AUDITION,
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
        # Handles all audition cases
        result = self.has_strong_title()
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

    @_log_to_bucket('strong_title')
    def has_strong_title(self):
        if self._has_wrong_meaning_for_style(self):
            return False

        # Some super-basic language specialization
        if self._has(keywords.ROMANCE):
            event_type = EVENT_TYPE_ROMANCE
            good_dance_event = GOOD_DANCE_EVENT_ROMANCE
        else:
            event_type = EVENT_TYPE
            good_dance_event = GOOD_DANCE_EVENT

        # Has "hiphop dance workshop/battle/audition"
        if self._title_has(good_dance_event):
            return "title has good_dance-event_type"

        # Has "workshop" and ("hiphop dance" or "moptop") and not "modern"
        # If the title contains a good keyword, and the body contains a bad keyword, this one will trigger (but the one below will not)
        if self._title_has(event_type) and self._title_has(GOOD_DANCE) and not self._title_has(BAD_DANCE_KEYWORDS):
            return "title has event_type, good and not bad keywords"

        # Has "workshop" and body has ("hiphop dance" but not "ballet")
        if self._title_has(event_type) and self._has(GOOD_DANCE) and not self._has(BAD_DANCE_KEYWORDS):
            return "title has event_type, body had good and not bad keywords"

        return False

    @_log_to_bucket('strong_body')
    def has_strong_body(self):
        if self._has_wrong_meaning_for_style(self):
            return False

        text = self._classified_event.processed_text.get_tokenized_text()

        # Some super-basic language specialization
        if self._has(keywords.ROMANCE):
            good_dance_event = GOOD_DANCE_EVENT_ROMANCE
        else:
            good_dance_event = GOOD_DANCE_EVENT

        # Body has "hiphop dance workshop" and body doesn't disqualify it ("modern dance")
        if self._has(good_dance_event) and not self._has(BAD_DANCE_KEYWORDS):
            return "body has good dance event, and title does not have bad keywords"

        # Or if there are bad keywords, lets see if we can find good keywords on a short line
        for line in text.split('\n'):
            pline = event_classifier.StringProcessor(line, self._classified_event.boundaries)
            # Skip the long bios with crap in them
            if len(line) > 500:
                continue
            pp = pline.has_token(good_dance_event)
            if pp:
                self._log('found strong event (%s) on short line: %s', pp, pline)
                return "body has short line containing good dance event"

        return False

    def has_list_of_good_classes(self):
        pass

    def has_many_street_styles(self):
        pass

    def has_standalone_keywords(self):
        pass
