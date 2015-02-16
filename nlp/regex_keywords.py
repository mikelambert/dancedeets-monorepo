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
    return prep_regex(inner_regex, matching=matching, word_boundaries=word_boundaries, match_cjk=match_cjk, wrapper=wrapper)

def prep_regex(regex_string, matching=False, word_boundaries=True, match_cjk=False, wrapper='%s'):
    if matching:
        regex_string = u'(' + regex_string + u')'
    else:
        regex_string = u'(?:' + regex_string + u')'
    if word_boundaries:
        if match_cjk:
            if not re2:
                regex_string = '(?u)%s' % regex_string
        else:
            regex_string = r"\b%s\b'?" % regex_string
    if wrapper:
        regex_string = wrapper % regex_string
    return regex_string

def make_regex_raw(regex_string, flags=0):
    if re2:
        # default max_mem is 8<<20 = 8*1000*1000
        return re.compile(regex_string, max_mem=60*1000*1000, flags=flags)
    else:
        return re.compile(regex_string, flags=flags)

def make_regex(strings, match_cjk, matching=False, wrapper='%s', flags=0):
    try:
        inner_regex = re_flatten.construct_regex(strings)
        regex = prep_regex(inner_regex, matching=matching, word_boundaries=True, match_cjk=match_cjk, wrapper=wrapper)
        return make_regex_raw(regex, flags)
    except UnicodeDecodeError:
        # When we compile a gigantic regex and fail, let's try to compile the component pieces and see where things fall apart
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


def make_regexes_raw(regex_string, wrapper='%s', flags=0):
    a = [None] * 2
    a[NO_WORD_BOUNDARIES] = make_regex_raw(prep_regex(regex_string, match_cjk=True, wrapper=wrapper), flags=flags)
    a[WORD_BOUNDARIES] = make_regex_raw(prep_regex(regex_string, match_cjk=False, wrapper=wrapper), flags=flags)
    return tuple(a)
