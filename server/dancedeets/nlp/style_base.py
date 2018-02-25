import logging

from dancedeets.nlp import event_types


class Style(object):
    """This is the basic API each style should export"""
    _classifier = None

    @classmethod
    def get_name(cls):
        raise NotImplementedError()

    @classmethod
    def get_popular_search_keywords(cls):
        raise NotImplementedError()

    @classmethod
    def get_rare_search_keywords(cls):
        raise NotImplementedError()

    @classmethod
    def get_all_keyword_event_types(cls):
        return event_types.EVENT_TYPES + cls.get_keyword_event_types()

    @classmethod
    def get_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        raise NotImplementedError()

    @classmethod
    def get_classifier(cls, other_style_regex=None):
        if other_style_regex is None:
            if cls._classifier is not None:
                return cls._classifier
            else:
                raise Exception('Expected %s classifier to be constructed already' % cls.get_name())
            pass
        else:
            logging.info('Initializing classifier for %s', cls.get_name())
            classifier = cls._get_classifier()
            classifier.vertical = cls.get_name()
            classifier.finalize_class(other_style_regex)
            cls._classifier = classifier
            return classifier

    @classmethod
    def get_basic_regex(cls):
        raise NotImplementedError()
