# -*-*- encoding: utf-8 -*-*-
#

from dancedeets.nlp import grammar
Any = grammar.Any
Name = grammar.Name

DANCE_STYLE_MISC = Any(
    'contratto mimo',  # italian contact mime
    'parkour',
    'disco dance',
    'disco tan\w+',  # czech disco dance
    'dance partner',
    'ghost',
    'ghosting',
    'acroyoga',
    'pilates',
    u'ピラティス',  # japanese pilates
)
