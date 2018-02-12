from . import grammar
from street import keywords
from street import rules


def _log_to_bucket(category):
    def wrap_func(func):
        def outer_func(self, *args, **kwargs):
            self._log_category = category
            try:
                result = func(self, *args, **kwargs)
                self._log('final result: %s', result)
            finally:
                self._log_category = None

        return outer_func

    return wrap_func


class DanceStyleEventClassifier(object):
    vertical = None

    def __init__(self, classified_event, debug=True):
        self.classified_event = classified_event
        self._debug = debug

        self._logs = {}
        self._log_category = None
        if not self.vertical:
            raise ValueError('Need to configure vertical')

    # utility methods
    def _title_has(self, keyword):
        return self.classified_event.processed_title.has_token(keyword)

    def _has(self, keyword):
        return self.classified_event.processed_text.has_token(keyword)

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

    def quick_is_dance_event(self):
        pass

    @_log_to_bucket('audition')
    def is_audition(self):
        if not self.quick_is_dance_event():
            return False

        # first check for audition in title
        has_audition = self._title_has(keywords.AUDITION)
        if has_audition:
            self._log('contains audition keyword: %s', has_audition)
        else:
            self._log('does not contain audition keyword')
            return False

        # now check for good keywords in title
        has_good_dance_title = self._title_has(rules.GOOD_DANCE)
        if has_good_dance_title:
            self._log('strong keyword in title: %s', has_good_dance_title)
            return True

        # now check for good keywords in title
        has_extended_good_crew_title = self._title_has(rules.MANUAL_DANCER[grammar.STRONG_WEAK])
        if has_extended_good_crew_title:
            self._log('strong crew in title: %s', has_extended_good_crew_title)
            return True

        # now check the body for good stuff and no bad stuff
        has_good_dance = self._has(rules.GOOD_DANCE)
        if has_good_dance:
            self._log('Has good dance style: %s', has_good_dance)
            has_wrong_style = self._has(rules.DANCE_WRONG_STYLE_TITLE)
            has_wrong_audition = self._has(keywords.WRONG_AUDITION)
            if has_wrong_style or has_wrong_audition:
                self._log('but has bad style (%s) or bad audition (%s)', has_wrong_style, has_wrong_audition)
                return False
            else:
                self._log('and no bad style or bad audition')

            return True

        return False

    def is_competition(self):
        pass

    def is_workshop(self):
        pass

    def has_list_of_good_classes(self):
        pass

    def has_good_event_title(self):
        pass

    def is_performance_or_practice(self):
        pass

    def has_many_street_styles(self):
        pass

    def has_standalone_keywords(self):
        pass
