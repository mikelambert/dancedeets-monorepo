# -*-*- encoding: utf-8 -*-*-
#

from . import grammar
Any = grammar.Any
Name = grammar.Name

DANCE_STYLE_CLASSICAL = Any(
    'contratto mimo',  # italian contact mime
    'class?ic[ao]',
    'tap',
    u'탭 ?댄스',  # korean tap dance
)

DANCE_STYLE_INDIAN = Any(
    'kalbeliya',
    'bhawai',
    'teratali',
    'ghumar',
    'kirtan',
    'indienne',
)

DANCE_STYLE_SEXY = Any(
    'exotic',
    'flirt danc\w+',
    u'폴 ?댄스',  # korean pole dance
    'go\W?go',
    'burlesque',
    u'バーレスク',  # japanese burlesque
)

DANCE_STYLE_MISC = Any(
    'parkour',
    'flamenco',
    'disco dance',
    'disco tan\w+',  # czech disco dance
    'dance partner',
    'hula',
    'ghost',
    'ghosting',
    'tumbling',
    'cheer',
    'butoh',
    u'舞踏',  # japanese butoh
    'persiana?',
    'arabe',
    'arabic',
    'araba',
    'oriental\w*',
    'oriente',
    'soca',
    'tahitian dancing',
    'tahitienne',
    'folklor\w+',
    'clogging',
    'acroyoga',
    'pilates',
    u'ピラティス',  # japanese pilates
    'zumba',
)
"""
    'artist\Win\Wresidence',
    'residency',
    'disciplinary',
    'reflective',
    'technique',
    'partnering',
    'guest artists?',
"""
