from dancedeets.nlp import all_styles_raw
from dancedeets.nlp import grammar
from dancedeets.nlp.styles import aerial_pole
from dancedeets.nlp.styles import african
from dancedeets.nlp.styles import ballet
from dancedeets.nlp.styles import ballroom
from dancedeets.nlp.styles import belly
from dancedeets.nlp.styles import bhangra
from dancedeets.nlp.styles import biodanza
from dancedeets.nlp.styles import bollywood
from dancedeets.nlp.styles import burlesque
from dancedeets.nlp.styles import capoeira
from dancedeets.nlp.styles import contact
from dancedeets.nlp.styles import contemporary
from dancedeets.nlp.styles import country
from dancedeets.nlp.styles import dancehall
from dancedeets.nlp.styles import discofox
from dancedeets.nlp.styles import exotic
from dancedeets.nlp.styles import five_rhythms
from dancedeets.nlp.styles import hustle
from dancedeets.nlp.styles import jazz
from dancedeets.nlp.styles import kpop
from dancedeets.nlp.styles import latin
from dancedeets.nlp.styles import modern
from dancedeets.nlp.styles import musical_theater
from dancedeets.nlp.styles import lion
from dancedeets.nlp.styles import partner_fusion
from dancedeets.nlp.styles import rockabilly
from dancedeets.nlp.styles import soulline
from dancedeets.nlp.styles import street
from dancedeets.nlp.styles import swing
from dancedeets.nlp.styles import tango
from dancedeets.nlp.styles import tap
from dancedeets.nlp.styles import wcs
from dancedeets.nlp.styles import zouk

# TODO: decide on Style vs Vertical
# Each import must have a Style that fits the base_styles.Style API
_STYLE_LIST = [
    aerial_pole.Style,
    african.Style,
    ballet.Style,
    ballroom.Style,
    belly.Style,
    bhangra.Style,
    biodanza.Style,
    bollywood.Style,
    burlesque.Style,
    capoeira.Style,
    contact.Style,
    contemporary.Style,
    country.Style,
    dancehall.Style,
    discofox.Style,
    exotic.Style,
    five_rhythms.Style,
    hustle.Style,
    jazz.Style,
    kpop.Style,
    latin.Style,
    modern.Style,
    musical_theater.Style,
    lion.Style,
    partner_fusion.Style,
    rockabilly.Style,
    soulline.Style,
    street.Style,
    swing.Style,
    tango.Style,
    tap.Style,
    wcs.Style,
    zouk.Style,
]

# Generate a keyed lookup of styles (for any name-dependent lookups from URLs)
# and ensure they are all unique.
STYLES = {}
for style in _STYLE_LIST:
    if style.get_name() in STYLES:
        raise ImportError('Style name duplicated: %s' % style.get_name())
    STYLES[style.get_name()] = style

misc_keyword_sets = [
    all_styles_raw.DANCE_STYLE_CLASSICAL,
    all_styles_raw.DANCE_STYLE_INDIAN,
    all_styles_raw.DANCE_STYLE_SEXY,
    all_styles_raw.DANCE_STYLE_MISC,
]


def all_styles_except(vertical):
    regexes = set()
    for regex_style in _STYLE_LIST:
        if regex_style != vertical:
            regexes.add(regex_style.get_basic_regex())
    regexes.update(misc_keyword_sets)
    return grammar.Any(*regexes)


# Classifiers need to generate a BAD_KEYWORDS of "other" styles of dance,
# which are dependent on having access to all the other styles of dance.
#
# So let's generate a regex of "other dance styles" for each style,
# and use it to construct a Classifer once (and all its associated regexes).
#
CLASSIFIERS = {}
for style in _STYLE_LIST:
    other_style_regex = all_styles_except(style.get_name())
    CLASSIFIERS[style.get_name()] = style.get_classifier(other_style_regex)
