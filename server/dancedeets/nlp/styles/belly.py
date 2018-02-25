# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

NON_BELLY_AMBIGUOUS_DANCE = Any(
    u'شرقي‎',  # arabic, but means 'oriental'
    u'بلدي‎',  # arabic, but means 'folk'
    # for an explanation of these, see http://www.shira.net/musings/dance-by-any-other-name.htm
    'oriental',  # oriental dance
    'egyptian',  # egyptian dance
    'middle eastern',  # middle eastern dance
)

BELLY = Any(
    'belly',
    'bauch',  # german
    'brzucha',  # polish
    'vi?entre',  # romance languages
    u'buik',  # danish
    u'肚皮',  # chinese
    u'ベリー',  # japanese
    u'배꼽',  # korean
    u'पेट',  # hindi
    u'बेली',  # hindi
    u'בטן',  # hebrew
)

REAL_DANCE = Any(
    commutative_connected(Any(BELLY, NON_BELLY_AMBIGUOUS_DANCE), dance_keywords.EASY_DANCE),
    'raqs sharqi',  # romanization of the arabic
    'raqs baladi',  # romanization of the arabic
    # for an explanation of these, see http://www.shira.net/musings/dance-by-any-other-name.htm
    'transnational fusion',
    commutative_connected(Any(u'tribal'), Any(u'fusi[oó]n\w*')),
    'bellycraft',
    'bellyfit',
    'its unmata',  # ITS unmata
)

RELATED_KEYWORDS = Any(
    'amy sigil',
    'unmata',
    'modern fusion',
    'isolat\w+',
    'sufi',
    'worldbellydancealliance',
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):

    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = NON_BELLY_AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(Classifier, self).is_dance_event()
        if result:
            return result

        return False


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'BELLY'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'bauch tanz',
            u'ריקודי בטן',
            u'肚皮',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'belly dance',
            'oriental dance',
            'egyptian dance',
            'middle eastern dance',
            'rasq sharqi',
            'tribal fusion',
            u'ベリーダンス',
            u'شرقي‎',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(BELLY, REAL_DANCE)
