# -*-*- encoding: utf-8 -*-*-
#

from . import all_styles_raw
from . import grammar
Any = grammar.Any
Name = grammar.Name

#TODO: Need to include AFRICAN in this!

DANCE_WRONG_STYLE = Name(
    'DANCE_WRONG_STYLE',
    Any(
        all_styles_raw.DANCE_STYLE_LATIN,
        all_styles_raw.DANCE_STYLE_SWING,
        all_styles_raw.DANCE_STYLE_TANGO,
        all_styles_raw.DANCE_STYLE_CLASSICAL,
        all_styles_raw.DANCE_STYLE_INDIAN,
        all_styles_raw.DANCE_STYLE_SEXY,
        all_styles_raw.DANCE_STYLE_BALLROOM,
        all_styles_raw.DANCE_STYLE_FUSION,
        all_styles_raw.DANCE_STYLE_CAPOEIRA,
        all_styles_raw.DANCE_STYLE_ZOUK,
        all_styles_raw.DANCE_STYLE_MISC,
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
