class Style(object):
    def __init__(self, index_name, public_name):
        self.index_name = index_name
        self.public_name = public_name

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
