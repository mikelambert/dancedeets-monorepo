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
