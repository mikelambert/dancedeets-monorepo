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
    commutative_connected(Any(BELLY, NON_BELLY_AMBIGUOUS_DANCE), keywords.EASY_DANCE),
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
)


class BellyClassifier(base_auto_classifier.DanceStyleEventClassifier):
    __metaclass__ = base_auto_classifier.AutoRuleGenerator

    vertical = event_types.VERTICALS.BELLY

    GOOD_DANCE = REAL_DANCE
    AMBIGUOUS_DANCE = NON_BELLY_AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True

    def is_dance_event(self):
        result = super(BellyClassifier, self).is_dance_event()
        if result:
            return result

        result = self.is_belly_dance()
        if result:
            return result

        return False

    @base_auto_classifier.log_to_bucket('is_belly_dance')
    def is_belly_dance(self):

        return False


def is_belly_event(classified_event):
    classifier = BellyClassifier(classified_event)
    return classifier.is_dance_event(), classifier.debug_info(), classifier.vertical
