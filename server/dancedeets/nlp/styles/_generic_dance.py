# -*-*- encoding: utf-8 -*-*-
#
# This is a "fake" Style/Classifier, just used to initiate searches
from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_search_keywords
from dancedeets.nlp import style_base


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    # No dance events
    def _quick_is_dance_event(self):
        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'GENERIC_DANCE'

    @classmethod
    def get_rare_search_keywords(cls):
        return dance_search_keywords.OBVIOUS_KEYWORDS

    @classmethod
    def get_popular_search_keywords(cls):
        return []

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return None
