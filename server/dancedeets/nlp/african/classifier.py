# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .. import base_auto_classifier
from .. import grammar
from ..street import keywords
from ..street import rules

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

REAL_DANCE = Any(
    # any dance can be an afro-dance!
    commutative_connected(Any('(?:african|afro)'), Any(keywords.DANCE_WRONG_STYLE, rules.STREET_STYLES)),
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

AMBIGUOUS_CONTACT = Name(
    'AMBIGUOUS_CONTACT',
    Any(
        'adowa',
        'aduma',
        'afr[iy][ck]?[ck]\w*',
        u'アフリカン',
        u'アフロ',
        u'非洲',
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
    )
)


class AfricanClassifier(base_auto_classifier.DanceStyleEventClassifier):
    vertical = event_types.VERTICALS.AFRICAN

    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = AMBIGUOUS_CONTACT
    ADDITIONAL_EVENT_TYPE = Any('congress',)

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(AfricanClassifier, self).is_dance_event()
        if result:
            return result

        return False


def is_african_event(classified_event):
    classifier = AfricanClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
