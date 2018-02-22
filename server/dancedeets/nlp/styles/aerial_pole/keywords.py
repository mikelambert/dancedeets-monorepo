from dancedeets.nlp import grammar

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

DANCE = Any(
    'pole-ates',
    'aerial\Whoop',
    'aerial\Wfabric',
)
AMBIUGOUS_DANCE = Any(
    'pole',
    'aerials?',
    'hoops?',
    'fabrics?',
    'silks?',
)
EVENT_TYPES = Any(
    'miss',  # miss pole dance
    'series',
)
