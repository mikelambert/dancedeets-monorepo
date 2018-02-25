# -*-*- encoding: utf-8 -*-*-
#

from . import grammar
Any = grammar.Any
Name = grammar.Name

DANCE_STYLE_SWING = Any(
    'balboa',
    'lindy',
    'lindyhop\w*',
    'east coast swing',
    u'リンディ',  # japanese lindy
    u'린디',  # korean lindy
    'swing',
    'charleston',
    'quickstep',
    'blues',
    u'ブルース',  # japanese blues
)

DANCE_STYLE_CLASSICAL = Any(
    'barre',
    'contato improv\w*',
    'contact improv\w*',
    u'コンタクトインプロビゼーション',  # japanese contact improv
    'contratto mimo',  # italian contact mime
    'limon',
    'modern dance',
    'jazz',
    u'재즈',  # korean jazz
    'contemporary',
    u'súčasný',  # contemporary slovak
    u'współczesnego',  # contemporary polish
    'contempor\w*',  # contemporary italian, french
    'class?ic[ao]',
    'tap',
    u'탭 ?댄스',  # korean tap dance
)

DANCE_STYLE_INDIAN = Any(
    'bollywood',
    u'볼리우드',  # bollywood
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

DANCE_STYLE_BALLROOM = Any(
    'waltz',
    u'왈츠',  # korean waltz
    u'ワルツ',  # japanese waltz
)

DANCE_STYLE_CAPOEIRA = Any(
    'capoeira',
    u'カポエイラ',  # japanese capoeira
)

DANCE_STYLE_MISC = Any(
    'parkour',
    'flamenco',
    'disco dance',
    'disco tan\w+',  # czech disco dance
    'dance partner',
    'hula',
    'hoop',
    'ghost',
    'ghosting',
    'tumbling',
    'cheer',
    'butoh',
    u'舞踏',  # japanese butoh
    'musical theat(?:re|er)',
    'persiana?',
    'arabe',
    'arabic',
    'araba',
    'oriental\w*',
    'oriente',
    'cubana',
    'soca',
    'tahitian dancing',
    'tahitienne',
    'folklor\w+',
    'artist\Win\Wresidence',
    'residency',
    'disciplinary',
    'reflective',
    'clogging',
    'acroyoga',
    'hoop\W?dance',
    'pilates',
    u'ピラティス',  # japanese pilates
    'zumba',
    'technique',
    'guest artists?',
    'partnering',
)
