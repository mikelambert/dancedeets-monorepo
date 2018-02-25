# TODO: clean up our module names
from dancedeets.nlp.styles import aerial_pole
from dancedeets.nlp.styles import african
from dancedeets.nlp.styles import belly
from dancedeets.nlp.styles import capoeira
from dancedeets.nlp.styles import contact
from dancedeets.nlp.styles import country
from dancedeets.nlp.styles import latin
from dancedeets.nlp.styles import partner_fusion
from dancedeets.nlp.styles import rockabilly
from dancedeets.nlp.styles import soulline
from dancedeets.nlp.styles import swing
from dancedeets.nlp.styles import tango
from dancedeets.nlp.styles import wcs
from dancedeets.nlp.styles import zouk

# TODO: decide on Style vs Vertical
# Each import must have a Style that fits the base_styles.Style API
_STYLE_LIST = [
    aerial_pole.Style,
    african.Style,
    belly.Style,
    capoeira.Style,
    contact.Style,
    country.Style,
    latin.Style,
    partner_fusion.Style,
    rockabilly.Style,
    soulline.Style,
    swing.Style,
    tango.Style,
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

#TODO: slowly migrate away from this dictionary in favor of Styles
from dancedeets import event_types
from dancedeets.nlp import all_styles_raw
from dancedeets.nlp import grammar
from dancedeets.nlp.street import rules
style_keywords = {
    event_types.VERTICALS.STREET: rules.STREET_STYLES,
    event_types.VERTICALS.BALLROOM: all_styles_raw.DANCE_STYLE_BALLROOM,
}
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
    #TODO: remove these eventually once the above dict is gone
    for regex_style in style_keywords:
        if regex_style != vertical:
            regexes.add(style_keywords[regex_style])
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
