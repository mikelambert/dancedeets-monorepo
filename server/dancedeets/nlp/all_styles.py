# -*-*- encoding: utf-8 -*-*-
#

from .. import grammar
Any = grammar.Any
Name = grammar.Name

DANCE_STYLE_LATIN = Any(
    'styling',
    'salsa',
    'bachata',
    'latin',
    'samba',
    u'サルサ',  # japanese salsa
    u'소스',  # korean salsa
    'latines',
    'rumba',
    'cha\W?cha',
    u'륨바',  # korean rumba
    'salsy',  # salsa czech
    'salser[oa]s?',
)

DANCE_STYLE_ZOUK = Any(
    'zouk',
    u'ズーク',  # japanese zouk
)
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

DANCE_STYLE_WCS = Any(
    'west coast swing',
    'wcs',
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

DANCE_STYLE_TANGO = Any(
    'tango',
    'milonga',
    u'タンゴ',  # japanese tango
    u'탱고',  # korean tango
)

DANCE_STYLE_SEXY = Any(
    'exotic',
    'pole danc\w+',
    'flirt danc\w+',
    u'ポールダンス',  # japanese pole dance
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

# Copied from the contact-improv classifier
CONTACT = '[ck]onta[ck]t\w*'
IMPROV = 'impro[wv]\w*'
DANCE_STYLE_CONTACT = Any(
    '%s\W?%s' % (CONTACT, IMPROV),
    grammar.commutative_connected(Any(IMPROV), Any(CONTACT)),
    u'接触即興',  # japanese
    u'即興接觸',  # chinese
    u'接觸即興',  # chinese
)

# Copied from country/classiifer
DANCE_STYLE_COUNTRY = Any(
    'country',
    'square',
    'contra',
    'texas shuffle',
    'clogging',
    'contredanse',
)

# Copied from rockabilly/classifier
DANCE_STYLE_ROCKABILLY = Any(
    'rockabilly',
    'jive\W?bop',
    'barn',
    'boogie\W?woogie',
    'rock\W?\W?(?:n|and|&|\+)\W?\W?roll\w*',
)

# Copied from soulline/classifier
DANCE_STYLE_SOULLINE = Any(
    'soul\W?line',
    '(?:baltimore|b\W?more)? linedance',
    'urban\W?line\W?dance',
)

DANCE_STYLE_BELLY = Any(
    'belly\W?danc(?:e(?:rs?)?|ing)',
    'belly\w*',
    'bellycraft',
    'worldbellydancealliance',
    u'ベリーダンス',  # japanese bellydance
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

DANCE_STYLE_FUSION = Any(
    'modern\W?jive',
    'ceroc',
    'leroc',
    'le-roc',
)

#TODO: Need to include AFRICAN in this!
DANCE_WRONG_STYLE = Name(
    'DANCE_WRONG_STYLE',
    Any(
        DANCE_STYLE_LATIN,
        DANCE_STYLE_SWING,
        DANCE_STYLE_TANGO,
        DANCE_STYLE_CLASSICAL,
        DANCE_STYLE_INDIAN,
        DANCE_STYLE_SEXY,
        DANCE_STYLE_BALLROOM,
        DANCE_STYLE_FUSION,
        DANCE_STYLE_CAPOEIRA,
        DANCE_STYLE_ZOUK,
        DANCE_STYLE_MISC,
    )
)

# These are okay to see in event descriptions, but we don't want it to be in the event title, or it is too strong for us
DANCE_WRONG_STYLE_TITLE_ONLY = Name(
    'DANCE_WRONG_STYLE_TITLE_ONLY',
    Any(
        # Sometimes used in studio name even though it's still a hiphop class:
        'ballroom',
        'ballet',
        'yoga',
        'talent shows?',  # we don't care about talent shows that offer dance options
        'stiletto',
        '\w{,10}(?:ball|bolu?)',  # basketball/baseball/football tryouts
        'pole',
    )
)

DANCE_WRONG_STYLE_TITLE = Name('DANCE_WRONG_STYLE_TITLE', Any(DANCE_WRONG_STYLE, DANCE_WRONG_STYLE_TITLE_ONLY))
