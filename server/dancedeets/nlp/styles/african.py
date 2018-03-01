# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base
from ..street import keywords
from ..street import rules

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    'urban kiz',
    'senegalese sabar',
    'joneeba african',
    u'coup[eé]\W?d[eé]cal[eé]',
    'adowa',
    u'aláàrìnjó',
    'agahu',
    'agbadza',
    'agbaei',
    'agbekor',
    'alingo',
    'ambasse bey',
    'assiko',
    'atilogwu',
    'azonto',
    'bamaaya',
    'bobaraba',
    'chakacha',
    'coladeira',
    'dhaanto',
    'eskista',
    'ewegh',
    'fendika',
    'fumefume',
    u'funaná',
    'hiragasy',
    'hlokoloza',
    'hunguhungu',
    'indlamu',
    'isicathulo',
    'kongobeat',
    'kpanlogo',
    'kwassa kwassa',
    'malivata',
    'mapouka',
    'mohobelo',
    'moribayasa',
    'muchongoyo',
    'muziki wa dansi',
    'mwanzele',
    'ndlamu',
    'ohangla',
    'okumkpa',
    'pantsula',
    'toyi-toyi',
    'xibelani',
    'yankadi',
)

AMBIGUOUS_AFRICAN = Name(
    'AMBIGUOUS_AFRICAN',
    Any(
        'adowa',
        'aduma',
        'afr[iy][ck]?[ck]\w*',
        u'αφρικ\w*',  # greek
        u'африк\w*',  # russian
        u'אפריקני',  # hebrew
        u'الأفريقي'  # arabic
        u'แอฟริกา',  # thai
        u'アフリカン',
        u'アフロ',
        u'非洲',
        u'아프리카\w*',
        u'아프리카 ?인?',  # korean
        'afrobeat',
        u'アフロビート',
        'afro\W?house',
        u'アフロハウス',
        'afro'
        'balante',
        'batuque',
        'borrowdale',
        'djembe',
        u'djolé',
        'etighi',
        'galala',
        u'guérewol',
        'gumboot',
        'kizomba',
        u'キゾンバ',
        'kuduro\w*',
        u'クドゥーロ',
        'kutiro',
        'makossa',
        'pat pat',
        'sabar',
        'serere',
        'sokkie',
        'suo',
        'tribal',
        'tufo',
        u'mand[ée]',
    )
)


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_AFRICAN
    ADDITIONAL_EVENT_TYPE = Any('congress',)

    # any dance can be an afro-dance!
    # afro-house, afro-salsa, afro-latin, etc
    # Something like:
    # cls.GOOD_DANCE = Any(cls.GOOD_DANCE, commutative_connected(Any('(?:african|afro)'), styles.all))

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
        return 'AFRICAN'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            'gumboot',
            'kpanlogo',
            'pantsula',
            'yankadi',
            'kpanlogo',
            'azonto',
            'coupé décalé',
            'adowa',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'senegalese sabar',
            'sabar',
            'african',
            'joneeba african',
            'kizomba',
            'kizomba dance',
            'kuduro',
            'kuduro dance',
            'african dance',
            'afrobeat dance',
            'アフリカンダンス',
            u'キゾンバ',
            u'クドゥーロ',
            u'非洲舞蹈',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(REAL_DANCE, AMBIGUOUS_AFRICAN)
