# -*-*- encoding: utf-8 -*-*-

import logging
try:
    import re2
    import re2 as re
except ImportError as e:
    logging.info("Could not import re2, falling back to re: %s", e)
    re2 = None
    import re

from . import grammar_matcher
from . import regex_keywords
from .street import keywords
from .street import rules


def find_competitor_list(search_text):
    processed_text = grammar_matcher.StringProcessor(search_text)
    results_match = re.search(r'\n0*1[^\d].+\n^0*2[^\d].+\n(?:^\d+.+\n){2,}', processed_text.text, re.MULTILINE)
    if results_match:
        numbered_list = results_match.group(0)
        num_lines = numbered_list.count('\n')
        if len(re.findall(r'\d ?[.:h] ?\d\d|\bam\b|\bpm\b', numbered_list)) > num_lines / 4:
            return None  # good list of times! workshops, etc! performance/shows/club-set times!
        processed_numbered_list = grammar_matcher.StringProcessor(numbered_list, processed_text.match_on_word_boundaries)
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
            if processed_text.match_on_word_boundaries == regex_keywords.WORD_BOUNDARIES:  # maybe separate on kana vs kanji?
                avg_words = 1.0 * sum([len([y for y in x.split(' ')]) for x in lines]) / num_lines
                if avg_words < 3:
                    return numbered_list
    return None


def get_schedule_line_groups(classified_event):
    text = classified_event.processed_text.get_tokenized_text()

    # (?!20[01][05])
    time = r'\b[012]?\d[:.,h]?(?:[0-5][05])?(?:am|pm)?\b'
    time_with_minutes = r'\b[012]?\d[:.,h]?(?:[0-5][05])(?:am|pm)?\b'
    time_to_time = r'%s ?(?:to|do|до|til|till|alle|a|-|–|[^\w,.]) ?%s' % (time, time)

    # We try to grab all lines in schedule up until schedule ends,
    # so we need a "non-schedule line at the end", aka ['']
    lines = text.split('\n') + ['']
    idx = 0
    schedule_lines = []
    while idx < len(lines):
        first_idx = idx
        while idx < len(lines):
            line = lines[idx]
            # if it has
            # grab time one and time two, store diff
            # store delimiters
            # maybe store description as well?
            # compare delimiters, times, time diffs, styles, etc
            times = re.findall(time_to_time, line)
            if not times or len(line) > 80:
                if idx - first_idx >= 1:
                    schedule_lines.append(lines[first_idx:idx])
                break
            idx += 1
        first_idx = idx
        while idx < len(lines):
            line = lines[idx]
            times = re.findall(time, line)
            # TODO(lambert): Somehow track "1)" that might show up here? :(
            times = [x for x in times if x not in ['1.', '2.']]
            if not times or len(line) > 80:
                if idx - first_idx >= 3:
                    schedule_lines.append(lines[first_idx:idx])
                break
            idx += 1
        idx += 1

    schedule_groups = []
    for sub_lines in schedule_lines:
        if not [x for x in sub_lines if re.search(time_with_minutes, x)]:
            continue
        schedule_groups.append(sub_lines)

    return schedule_groups
