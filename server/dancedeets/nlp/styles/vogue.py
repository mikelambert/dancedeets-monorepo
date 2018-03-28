# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import event_types
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.street import keywords

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    COMBINED_KEYWORDS = Any(
        keywords.VOGUE,
        keywords.VOGUE_EVENT,
        keywords.EASY_VOGUE,
        keywords.TOO_EASY_VOGUE,
    )

    @base_auto_classifier.log_to_bucket('has_any_relevant_keywords')
    def _has_any_relevant_keywords(self):
        # Override this here.
        # Don't use the other_bad_regex and GOOD/AMBIGUOUS keywords
        return self._has(self.COMBINED_KEYWORDS)

    @base_auto_classifier.log_to_bucket('is_dance_event')
    def is_dance_event(self):
        self._log('Starting %s classifier', self.vertical)

        if not self._has_any_relevant_keywords():
            self._log('does not have any relevant keywords for this style')
            return False

        from dancedeets.nlp.street import classifier
        is_vogue = classifier.is_vogue_event(self._classified_event)
        self._log(is_vogue[1])

        if is_vogue[0]:
            return 'has vogue keywords'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'VOGUE'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'mini ball',
            'vogue ball',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'vogue',
            'vogue dance',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return event_types.STREET_EVENT_TYPES

    @classmethod
    def _get_classifier(cls):
        return Classifier
