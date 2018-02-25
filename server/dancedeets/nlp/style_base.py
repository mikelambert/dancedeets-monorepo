import logging


class Style(object):
    """This is the basic API each style should export"""

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
    def get_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        raise NotImplementedError()

    @classmethod
    def get_classifier(cls, other_style_regex):
        logging.info('Initializing classifier for %s', cls.get_name())
        classifier = cls._get_classifier()
        classifier.vertical = cls.get_name()
        print 0, classifier, classifier.finalize_class
        classifier.finalize_class(other_style_regex)
        return classifier

    @classmethod
    def get_basic_regex(cls):
        raise NotImplementedError()
