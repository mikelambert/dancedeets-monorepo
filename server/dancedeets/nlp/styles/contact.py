# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

CONTACT = Any(
    '[ck]onta[ck]t\w*',
    u'контактная',
)
IMPROV = Any(
    'impro(?:[wv]\w*)?',
    u'импровизация',
)

REAL_DANCE = Any(
    commutative_connected(Any(IMPROV), Any(CONTACT)),
    u'接触即興',  # japanese
    u'即興接觸',  # chinese
    u'接觸即興',  # chinese
)

AMBIGUOUS_CONTACT = Name('AMBIGUOUS_CONTACT', Any(
    CONTACT,
    '[ck]i',
    '[ck]\W?i\W?',
))

KEYWORDS = Name(
    'KEYWORDS', Any(
        'contact'
        'connection'
        'weight',
        'momentum',
        'movement',
        'mover',
        'trust',
        'balance',
        'support',
        'bodies',
        'body',
    )
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = REAL_DANCE
    # Too many false positives
    # AMBIGUOUS_DANCE = AMBIGUOUS_CONTACT
    ADDITIONAL_EVENT_TYPE = Any(
        'jam',
        u'dżemów',
        'lab',
        'festival',
    )

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        result = self.is_ci_dance()
        if result:
            return result

        return False

    @base_auto_classifier.log_to_bucket('is_ci_dance')
    def is_ci_dance(self):
        title_is_ambiguous = self._title_has(AMBIGUOUS_CONTACT)
        has_contact_improv = self._has(self.GOOD_DANCE_FULL)
        num_keywords = len(set(self._get(KEYWORDS))) + len(set(self._get(dance_keywords.EASY_DANCE)))
        if title_is_ambiguous and has_contact_improv:
            return 'title has CI/contact, body has contact improv'

        if title_is_ambiguous and num_keywords >= 2:
            return 'title has CI/contact, body has relevant bits'

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'CONTACT'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'kontaktní improvizace',
            'kontaktimprovisation',
            '即興接觸',
            'contacto improvisación',
            'improvisacion de contacto',
            'ci with',
            'ci class',
            'ci jam',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'contact improv',
            'contact improvisaton',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return REAL_DANCE
