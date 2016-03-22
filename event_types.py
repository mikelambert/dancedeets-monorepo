class EventType(object):
    def __init__(self, index_name, public_name, public_name_plural):
        self.index_name = index_name
        self.public_name = public_name
        self.public_name_plural = public_name_plural

    def __repr__(self):
        return 'EventType(%s, %s, %s)' % (self.index_name, self.public_name, self.public_name_plural)

    @property
    def url_name(self):
        return self.public_name.lower()

BATTLE = EventType('BATTLE', 'Competition', 'Competitions')
PERFORMANCE = EventType('PERFORMANCE', 'Performance', 'Performances')
WORKSHOP = EventType('WORKSHOP', 'Workshop', 'Workshops')
PARTY = EventType('PARTY', 'Party', 'Parties')
SESSION = EventType('SESSION', 'Session', 'Sessions')
AUDITION = EventType('AUDITION', 'Audition', 'Auditions')
REGULAR_CLASS = EventType('REGULAR_CLASS', 'Regular Class', 'Regular Classes')

EVENT_TYPES = [
    BATTLE,
    PERFORMANCE,
    PARTY,
    WORKSHOP,
    SESSION,
    AUDITION,
    REGULAR_CLASS,
]


class Style(object):
    def __init__(self, index_name, public_name):
        self.index_name = index_name
        self.public_name = public_name

    def __repr__(self):
        return 'Style(%s, %s)' % (self.index_name, self.public_name)

    @property
    def url_name(self):
        return self.public_name.lower()

BREAK = Style('BREAK', 'Breaking')
HIPHOP = Style('HIPHOP', 'Hip-Hop')
HOUSE = Style('HOUSE', 'House')
POP = Style('POP', 'Popping')
LOCK = Style('LOCK', 'Locking')
WAACK = Style('WAACK', 'Waacking')
DANCEHALL = Style('DANCEHALL', 'Dancehall')
VOGUE = Style('VOGUE', 'Vogue')
KRUMP = Style('KRUMP', 'Krumping')
TURF = Style('TURF', 'Turfing')
LITEFEET = Style('LITEFEET', 'Litefeet')
FLEX = Style('FLEX', 'Flexing')
BEBOP = Style('BEBOP', 'Bebop')
ALLSTYLE = Style('ALLSTYLE', 'All-Styles')

STYLES = [
    BREAK,
    HIPHOP,
    HOUSE,
    POP,
    LOCK,
    WAACK,
    DANCEHALL,
    VOGUE,
    KRUMP,
    TURF,
    LITEFEET,
    FLEX,
    BEBOP,
    ALLSTYLE,
]

CATEGORY_LOOKUP = dict([(x.index_name, x.public_name) for x in STYLES + EVENT_TYPES])


def humanize_categories(categories):
    return [CATEGORY_LOOKUP[x] for x in categories]
