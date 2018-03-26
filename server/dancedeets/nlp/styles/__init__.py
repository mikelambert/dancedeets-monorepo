import importlib
import logging

from dancedeets.nlp import all_styles_raw
from dancedeets.nlp import grammar

STYLE_NAMES = [
    '_generic_dance',
    'aerial_pole',
    'african',
    'afro_cuban',
    'american_tango',
    'bachata',
    'ballet',
    'ballroom',
    'belly',
    'bhangra',
    'biodanza',
    'bolero',
    'bollywood',
    'bokwa',
    'bugg',
    'burlesque',
    'butoh',
    'cancan',
    'capoeira',
    'chacha',
    'cheer',
    'chicago_stepping',
    'clogging',
    'contact',
    'contemporary',
    'country',
    'country_two_step',
    'dancehall',
    'dc_hand',
    'detroit_ballroom',
    'discofox',
    'east_coast_swing',
    'exotic',
    'five_rhythms',
    'flamenco',
    'folk',
    'forro',
    'hamachacha',
    'hula',
    'hulahoop',
    'hustle',
    'indian',
    'irish',
    'jazz',
    'jive',
    'kizomba',
    'kompa',
    'kpop',
    'latin',
    'lion',
    'majorette',
    'mambo',
    'merengue',
    'modern',
    'musical_theater',
    'northern_soul',
    'partner_fusion',
    'paso_doble',
    'poi_staff',
    'polka',
    'quickstep',
    'rockabilly',
    'rumba',
    'samba',
    'soulline',
    'street',
    'swing',
    'tango',
    'tap',
    'viennese_waltz',
    'waltz',
    'wcs',
    'zapateado',
    'zouk',
    'zumba',
    'zydeco',
]

_STYLE_LIST = []

# TODO: decide on Style vs Vertical
# Each import must have a Style that fits the base_styles.Style API
for style_name in STYLE_NAMES:
    module = importlib.import_module('dancedeets.nlp.styles.%s' % style_name)
    _STYLE_LIST.append(module.Style)

# Generate a keyed lookup of styles (for any name-dependent lookups from URLs)
# and ensure they are all unique.
STYLES = {}
for style in _STYLE_LIST:
    if style.get_name() in STYLES:
        raise ImportError('Style name duplicated: %s' % style.get_name())
    STYLES[style.get_name()] = style
    try:
        # Ensure we can iterate over everything we need:
        for x in style.get_all_keyword_event_types():
            pass
        # Ensure we can iterate over everything we need:
        for x in style.get_search_keyword_event_types():
            pass
        # Ensure we can iterate over everything we need:
        for x in style.get_popular_search_keywords():
            pass
        # Ensure we can iterate over everything we need:
        for x in style.get_rare_search_keywords():
            pass
    except:
        logging.exception('Verifying style %s is iterable' % style.get_name())
        raise

misc_keyword_sets = [
    all_styles_raw.DANCE_STYLE_MISC,
]


def all_styles_except(vertical):
    regexes = set()
    for regex_style in _STYLE_LIST:
        if regex_style.get_name() != vertical:
            regex = regex_style.get_cached_basic_regex()
            if regex:
                regexes.add(regex)
    regexes.update(misc_keyword_sets)
    return regexes


# Classifiers need to generate a BAD_KEYWORDS of "other" styles of dance,
# which are dependent on having access to all the other styles of dance.
#
# So let's generate a regex of "other dance styles" for each style,
# and use it to construct a Classifier once (and all its associated regexes).
#
CLASSIFIERS = {}
for style in _STYLE_LIST:
    other_style_regexes = all_styles_except(style.get_name())
    CLASSIFIERS[style.get_name()] = style.get_classifier(other_style_regexes)

_global_preprocess_removal = {}
for style in _STYLE_LIST:
    for language, rule in style.get_preprocess_removal().iteritems():
        if language not in _global_preprocess_removal:
            _global_preprocess_removal[language] = []
        _global_preprocess_removal[language].append(rule)

PREPROCESS_REMOVAL = {}
for language, rules in _global_preprocess_removal.iteritems():
    PREPROCESS_REMOVAL[language] = grammar.Name('PREPROCESS_REMOVAL_%s' % language, grammar.Any(*rules))
