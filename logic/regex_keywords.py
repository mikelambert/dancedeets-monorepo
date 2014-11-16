#


import logging
try:
    import re2
    import re2 as re
except ImportError:
    logging.info("Could not import re2, falling back to re.")
    re2 = None
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)
from util import re_flatten

def make_regex_string(strings, matching=False, word_boundaries=False, match_cjk=False, wrapper='%s'):
    inner_regex = re_flatten.construct_regex(strings)
    if matching:
        regex = u'(' + inner_regex + u')'
    else:
        regex = u'(?:' + inner_regex + u')'
    if word_boundaries:
        if match_cjk and not re2:
            regex = '(?u)%s' % regex
        else:
            regex = r'\b%s\b' % regex
    regex = wrapper % regex
    return regex


def make_regex(strings, match_cjk, matching=False, wrapper='%s', flags=0):
    try:
        regex = make_regex_string(strings, matching=matching, word_boundaries=True, match_cjk=match_cjk, wrapper=wrapper)
        if re2:
            # default max_mem is 8<<20 = 8*1000*1000
            return re.compile(regex, max_mem=60*1000*1000, flags=flags)
        else:
            return re.compile(regex, flags=flags)
    except UnicodeDecodeError:
        for line in strings:
            try:
                re.compile(u'|'.join([line]), re.UNICODE)
            except UnicodeDecodeError:
                logging.error("failed to compile: %r: %s", line, line)
                raise
        logging.fatal("Error constructing regexes")

NO_WORD_BOUNDARIES = 0
WORD_BOUNDARIES = 1
def make_regexes(strings, matching=False, wrapper='%s', flags=0):
    a = [None] * 2
    a[NO_WORD_BOUNDARIES] = make_regex(strings, matching=matching, match_cjk=True, wrapper=wrapper, flags=flags)
    a[WORD_BOUNDARIES] = make_regex(strings, matching=matching, match_cjk=False, wrapper=wrapper, flags=flags)
    return tuple(a)
