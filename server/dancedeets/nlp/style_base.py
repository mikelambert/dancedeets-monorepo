# This is the basic API each style should export


class Style(object):
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
    def get_classifier(cls, other_style_regex):
        raise NotImplementedError()

    @classmethod
    def get_basic_regex(cls):
        raise NotImplementedError()
