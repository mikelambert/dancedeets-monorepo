def should_show(e):
    return not e.verticals or 'STREET' in e.verticals


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
    def __init__(self, index_name, public_name, categories_name=None):
        self.index_name = index_name
        self.public_name = public_name
        self.categories_name = categories_name or self.index_name

    def __repr__(self):
        return 'Style(%s, %s, %s)' % (self.index_name, self.public_name, self.categories_name)

    @property
    def url_name(self):
        return self.public_name.lower()


BREAK = Style('BREAKING', 'Breaking', categories_name='BREAK')
HIPHOP = Style('HIPHOP', 'Hip-Hop')
HOUSE = Style('HOUSE', 'House')
POP = Style('POPPING', 'Popping', categories_name='POP')
LOCK = Style('LOCKING', 'Locking', categories_name='LOCK')
WAACK = Style('WAACKING', 'Waacking', categories_name='WAACK')
DANCEHALL = Style('DANCEHALL', 'Dancehall')
VOGUE = Style('VOGUE', 'Vogue')
KRUMP = Style('KRUMPING', 'Krumping', categories_name='KRUMP')
TURF = Style('TURFING', 'Turfing', categories_name='TURF')
LITEFEET = Style('LITEFEET', 'Litefeet')
FLEX = Style('FLEXING', 'Flexing', categories_name='FLEX')
BEBOP = Style('BEBOP', 'Bebop')
ALLSTYLE = Style('ALLSTYLE', 'All-Styles')
KIDS = Style('KIDS', 'Kids')
STREET = Style('STREET', 'Street Dance')

STYLES = [
    STREET,
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
    KIDS,
]

CATEGORY_LOOKUP = dict([(x.index_name, x.public_name) for x in STYLES + EVENT_TYPES])


def humanize_categories(categories):
    return [CATEGORY_LOOKUP[x] for x in categories]
