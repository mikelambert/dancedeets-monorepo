# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from dancedeets.nlp.street import keywords
from dancedeets.nlp.street import rules

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    COMBINED_KEYWORDS = Any(
        keywords.AMBIGUOUS_DANCE_MUSIC,
        rules.STREET_STYLES,
    )

    @base_auto_classifier.log_to_bucket('has_any_relevant_keywords')
    def _has_any_relevant_keywords(self):
        # Has at least one of the major keywords we're expecting
        return self._has(self.COMBINED_KEYWORDS)

    @classmethod
    def finalize_class(cls, other_style_regex):
        pass

    def is_dance_event(self):
        self._log('Starting %s classifier', self.vertical)

        if not self._has_any_relevant_keywords():
            self._log('does not have any relevant keywords for this style')
            return False

        #TODO: until we fix our delay-load import problems
        from dancedeets.nlp.street import classifier
        result = classifier.is_street_event(self._classified_event)
        self._logs = [result[1]]
        return result[0]


def two(w):
    a, b = w.split(' ')
    keyword_list = [
        '%s %s' % (a, b),
        '%s%s' % (a, b),
    ]
    return keyword_list


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'STREET'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'bboys',
            'bboying',
            'bgirl',
            'bgirls',
            'bgirling',
            'breakdancing',
            'breakdancers',
            'breakdanse',
            'hiphop',
            'hip hop',
            'new style',
            'house danse',
            'afro house',
            'afrohouse',
            'poppers',
            'poplock',
            'tutting',
            'bopping',
            'boppers',
            'lockers',
            'locking',
            'waacking',
            'waackers',
            'waack',
            'whacking',
            'whackers',
            'jazzrock',
            'jazz rock',
            'jazz-rock',
            'ragga jam',
            'krump',
            'krumperz',
            'krumping',
            'streetjazz',
            'voguing',
            'house danse',
            'hiphop dance',
            'hiphop danse',
            'hip hop danse',
            'tous style',
            'urban dance',
            'afro house',
            'urban style',
            'turfing',
            'baile urbano',
            'soul dance',
            'footwork',
            '7 to smoke',
            u'ストリートダンス',
            u'ブレックダンス',
            'cypher',
            'cypher battle',
            'cypher jam',
        ] + two('electro dance') + two('lite feet')

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'bboy',
            'breaking',
            'breakdance',
            'house dance',
            'bebop',
            'dancehall',
            'street jazz',
            'street-jazz',
            'hip hop dance',
            # 'house workshop'....finds auto-add events we don't want labelled as house or as dance events
            # so we don't want to list it here..
            #'waving',
            #'boogaloo',
            # 'uk jazz', 'uk jazz', 'jazz fusion',
            # 'flexing',
            'lock',
            'popping',
            'dance',
            'choreo',
            'choreography',
            #'kpop', 'k pop',
            'vogue',
            'all styles',
            'freestyle',
        ] + two('hip hop') + two('street dance') + two('new style') + two('all styles')

    @classmethod
    def get_search_keyword_event_types(cls):
        return [
            'battle',
            'jam',
            'bonnie and clyde',
        ]

    @classmethod
    def _get_classifier(cls):
        return Classifier
