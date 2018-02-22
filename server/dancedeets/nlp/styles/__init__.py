# TODO: clean up our module names
from aerial_pole import classifier as aerial_pole_classifier

# TODO: decide on Style vs Vertical
# Each import must have a Style that fits the base_styles.Style API
_STYLE_LIST = [
    aerial_pole_classifier.Style,
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
from dancedeets.nlp import grammar
from dancedeets.nlp.street import rules
from dancedeets.nlp.street import keywords
style_keywords = {
    event_types.VERTICALS.STREET: rules.STREET_STYLES,
    event_types.VERTICALS.LATIN: keywords.DANCE_STYLE_LATIN,
    event_types.VERTICALS.SWING: keywords.DANCE_STYLE_SWING,
    event_types.VERTICALS.TANGO: keywords.DANCE_STYLE_TANGO,
    event_types.VERTICALS.CAPOEIRA: keywords.DANCE_STYLE_CAPOEIRA,
    event_types.VERTICALS.BALLROOM: keywords.DANCE_STYLE_BALLROOM,
    event_types.VERTICALS.ZOUK: keywords.DANCE_STYLE_ZOUK,
    event_types.VERTICALS.WCS: keywords.DANCE_STYLE_WCS,
    event_types.VERTICALS.PARTNER_FUSION: keywords.DANCE_STYLE_FUSION,
    event_types.VERTICALS.ROCKABILLY: keywords.DANCE_STYLE_ROCKABILLY,
    event_types.VERTICALS.COUNTRY: keywords.DANCE_STYLE_COUNTRY,
    event_types.VERTICALS.CONTACT: keywords.DANCE_STYLE_CONTACT,
    event_types.VERTICALS.AFRICAN: keywords.DANCE_STYLE_AFRICAN,
    event_types.VERTICALS.BELLY: keywords.DANCE_STYLE_BELLY,
    event_types.VERTICALS.SOULLINE: keywords.DANCE_STYLE_SOULLINE,
}
misc_keyword_sets = [
    keywords.DANCE_STYLE_CLASSICAL,
    keywords.DANCE_STYLE_INDIAN,
    keywords.DANCE_STYLE_SEXY,
    keywords.DANCE_STYLE_MISC,
]


def all_styles_except(vertical):
    regexes = set()
    for regex_style in _STYLE_LIST:
        if regex_style != style:
            regexes.add(regex_style.get_basic_regex())
    #TODO: remove these eventually once the above dict is gone
    for regex_style in style_keywords:
        if regex_style != style:
            regexes.add(style_keywords[regex_style])
    regexes.update(misc_keyword_sets)
    return grammar.Any(*regexes)


# This is a function for now, while we work through the migration issues causing import problems
# TODO: move this back inline to make it a global, once the above dict is gone
def get_classifiers():
    # Classifiers need to generate a BAD_KEYWORDS of "other" styles of dance,
    # which are dependent on having access to all the other styles of dance.
    #
    # So let's generate a regex of "other dance styles" for each style,
    # and use it to construct a Classifer once (and all its associated regexes).
    #
    CLASSIFIERS = []
    for style in _STYLE_LIST:
        other_style_regex = all_styles_except(style.get_name())
        CLASSIFIERS.append(style.get_classifier(other_style_regex))
    return CLASSIFIERS
