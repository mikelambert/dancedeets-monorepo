import logging
try:
    import re2
    import re2 as re
except ImportError as e:
    logging.info("Could not import re2, falling back to re: %s", e)
    re2 = None
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)
from . import cjk_detect

def cjk_adjacent():
    """Since we find it too difficult to match \b in CJK text, let's let any CJK character count as a boundary."""
    cjk_char = cjk_detect.cjk_regex_string
    return '(?:(?=%(char)s)|(?<=%(char)s))' % {'char': cjk_char}

_CJK_ADJACENT_STRING = cjk_adjacent()

def _wrap_regex(regex_string, matching=False, word_boundaries=True, match_cjk=False, wrapper='%s'):
    if matching:
        regex_string = u'(' + regex_string + u')'
    else:
        regex_string = u'(?:' + regex_string + u')'
    if word_boundaries:
        if match_cjk:
            if not re2:
                regex_string = '(?u)%s' % regex_string
            regex_string = r"(?:\b|%s)%s(?:\b|%s)" % (_CJK_ADJACENT_STRING, regex_string, _CJK_ADJACENT_STRING)
        else:
            regex_string = r"\b%s\b'?" % regex_string
    if wrapper:
        regex_string = wrapper % regex_string
    return regex_string

def _compile_regex(regex_string, flags=0):
    try:
        if re2:
            # default max_mem is 8<<20 = 8*1000*1000
            return re.compile(regex_string, max_mem=60*1000*1000, flags=flags)
        else:
            return re.compile(regex_string, flags=flags)
    except:
        logging.exception("Error compiling with flags %s for string: %s", flags, regex_string)
        raise

NO_WORD_BOUNDARIES = 0
WORD_BOUNDARIES = 1
def make_regexes_raw(regex_string, matching=False, wrapper='%s', flags=0):
    a = [None] * 2
    a[NO_WORD_BOUNDARIES] = _compile_regex(_wrap_regex(regex_string, matching=matching, match_cjk=True, wrapper=wrapper), flags=flags)
    a[WORD_BOUNDARIES] = _compile_regex(_wrap_regex(regex_string, matching=matching, match_cjk=False, wrapper=wrapper), flags=flags)
    return tuple(a)
