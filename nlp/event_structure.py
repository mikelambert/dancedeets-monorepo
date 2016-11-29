# -*-*- encoding: utf-8 -*-*-

import logging
try:
    import re2
    import re2 as re
except ImportError as e:
    logging.info("Could not import re2, falling back to re: %s", e)
    re2 = None
    import re

from . import event_classifier
from . import keywords
from . import regex_keywords
from . import rules


def find_competitor_list(search_text):
    processed_text = event_classifier.StringProcessor(search_text)
    results_match = re.search(r'\n0*1[^\d].+\n^0*2[^\d].+\n(?:^\d+.+\n){2,}', processed_text.text, re.MULTILINE)
    if results_match:
        numbered_list = results_match.group(0)
        num_lines = numbered_list.count('\n')
        if len(re.findall(r'\d ?[.:h] ?\d\d|\bam\b|\bpm\b', numbered_list)) > num_lines / 4:
            return None # good list of times! workshops, etc! performance/shows/club-set times!
        processed_numbered_list = event_classifier.StringProcessor(numbered_list, processed_text.match_on_word_boundaries)
        event_keywords = processed_numbered_list.get_tokens(rules.EVENT)
        if len(event_keywords) > num_lines / 8:
            return None
        if processed_text.has_token(keywords.WRONG_NUMBERED_LIST):
            return None
        if num_lines > 10:
            return numbered_list
        else:
            lines = numbered_list.split('\n')
            qualified_lines = len([x for x in lines if re.search(r'[^\d\W].*[-(]', x)])
            if qualified_lines > num_lines / 2:
                return numbered_list
            for type in ['crew', 'pop|boog', 'lock', 'b\W?(?:boy|girl)']:
                qualified_lines = len([x for x in lines if re.search(type, x)])
                if qualified_lines > num_lines / 8:
                    return numbered_list
            if processed_text.match_on_word_boundaries == regex_keywords.WORD_BOUNDARIES: # maybe separate on kana vs kanji?
                avg_words = 1.0 * sum([len([y for y in x.split(' ')]) for x in lines]) / num_lines
                if avg_words < 3:
                    return numbered_list
    return None
