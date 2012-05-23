import re

from logic import event_classifier

bad_battles = [
    'talent',
    'beatbox',
    'rap',
    'swimsuit',
    'street fighter',
    'tekken',
    'capcom',
    'games?',
    'game breaking',
    'videogames?',
    'sexy',
    'lingerie',
    'sing',
    'judge jules',
]
wrong_battle_styles = [
    'emcee',
    'rap',
    'beat',
    'dj',
    'producer',
    'performance',
    'graf(?:fiti)?',
]
p1 = event_classifier.make_regex_string(wrong_battle_styles)
p2 = event_classifier.make_regex_string(event_classifier.battle_keywords)
bad_battles.append(u'%s %s' % (p1, p2))
bad_battles.append(u'%s %s' % (p1, p2))
bad_battles_regex = event_classifier.make_regexes(bad_battles)

p1 = event_classifier.make_regex_string(event_classifier.easy_dance_keywords)
p2 = event_classifier.make_regex_string(event_classifier.battle_keywords)
dance_battles_regex = event_classifier.make_regexes([
    u'%s %s' % (p1, p2),
    u'%s %s' % (p2, p1),
])
assert dance_battles_regex[1].search('dance battle')

non_dance_support = [
    'fundraiser',
    'likes?',
    'votes?',
    'support',
]
non_dance_regex = event_classifier.make_regexes(non_dance_support)

def find_competitor_list(classified_event):
    text = classified_event.search_text
    results = re.search(r'0*1[^\d].+\n^0*2[^\d].+\n(?:^\d+.+\n){2,}', text, re.MULTILINE)
    if results:
        numbered_list = results.group(0)
        num_lines = numbered_list.count('\n')
        if len(re.findall(r'\d ?[.:] ?\d\d|am|pm', numbered_list)) > num_lines / 4:
            return False # good list of times! workshops, etc! performance/shows/club-set times!
        if len(event_classifier.all_regexes['event_regex'][classified_event.boundaries].findall(numbered_list)) > num_lines / 8:
            return False
        if num_lines > 10:
            return True
        else:
            lines = numbered_list.split('\n')
            qualified_lines = len([x for x in lines if re.search(r'[^\d\W].*[-(]', x)])
            if qualified_lines > num_lines / 2:
                return True
            for type in ['crew', 'pop|boog', 'lock', 'b\W?(?:boy|girl)']:
                qualified_lines = len([x for x in lines if re.search(type, x)])
                if qualified_lines > num_lines / 8:
                    return True
            if classified_event.boundaries == event_classifier.WORD_BOUNDARIES: # maybe separate on kana vs kanji?
                avg_words = 1.0 * sum([len([y for y in x.split(' ')]) for x in lines]) / num_lines
                if avg_words < 3:
                    return True
    return False

def is_battle(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')
    has_competitors = find_competitor_list(classified_event)
    if not has_competitors and classified_event.calc_inverse_keyword_density >= 5:
        return (False, 'relevant keywords too sparse')
    if not classified_event.real_dance_matches and not classified_event.manual_dance_keywords_matches:
        return (False, 'no strong dance keywords')
    search_text = classified_event.final_search_text

    if dance_battles_regex[classified_event.boundaries].search(search_text):
        if not non_dance_regex[classified_event.boundaries].search(classified_event.final_title):
            if not event_classifier.all_regexes['dance_wrong_style_title_regex'][classified_event.boundaries].search(classified_event.final_title):
                return (True, 'good-style real dance battle/comp!')
    if has_competitors:
                if len(set(classified_event.real_dance_matches + classified_event.manual_dance_keywords_matches)) > 1:
                        return (True, 'has a list of competitors, and some strong dance keywords')

    if event_classifier.all_regexes['battle_regex'][classified_event.boundaries].search(search_text):
        if event_classifier.all_regexes['n_x_n_regex'][classified_event.boundaries].search(search_text):
            if not bad_battles_regex[classified_event.boundaries].search(search_text):
                return (True, 'battle keyword, NxN, good dance style')

    if event_classifier.all_regexes['start_judge_keywords_regex'][classified_event.boundaries].search(search_text):
        if not bad_battles_regex[classified_event.boundaries].search(search_text):
            return (True, 'no ambiguous wrong-battle-style keywords')
        elif len(set(classified_event.real_dance_matches + classified_event.manual_dance_keywords_matches)) > 1:
            return (True, 'had some ambiguous keywords, but enough strong dance matches anyway')
        # remove this if we add another clause below this. or implement an aggregated-reason
        return (False, 'too ambiguous of a judge/jury result')
    return (False, 'no judge/jury or battle/NxN')

