# -*-*- encoding: utf-8 -*-*-
#

from . import grammar
Any = grammar.Any
Name = grammar.Name

DANCE_STYLE_CLASSICAL = Any(
    'contratto mimo',  # italian contact mime
)

DANCE_STYLE_MISC = Any(
    'parkour',
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
    'soca',
    'tahitian dancing',
    'tahitienne',
    'folklor\w+',
    'clogging',
    'acroyoga',
    'pilates',
    u'ピラティス',  # japanese pilates
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
