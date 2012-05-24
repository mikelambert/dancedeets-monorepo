import re

from logic import event_classifier

bad_battles = [
    'talent',
    'beatbox',
    'rap',
    'swimsuit',
    'tekken',
    'capcom',
    'games?',
    'game breaking',
    'videogames?',
    'sexy',
    'lingerie',
    'judge jules',
]
wrong_battle_styles = [
    '(?:mc|emcee)\Whip\W?hop',
    'emcee',
    'rap',
    'beat',
    'beatbox',
    'dj\W?s?',
    'producer',
    'performance',
    'graf(?:fiti)?',
]
p1 = event_classifier.make_regex_string(wrong_battle_styles)
p2 = event_classifier.make_regex_string(event_classifier.battle_keywords + event_classifier.n_x_n_keywords + event_classifier.contest_keywords)
bad_battles.append(u'%s ?%s' % (p1, p2))
bad_battles.append(u'%s ?%s' % (p1, p2))
bad_battles_regex = event_classifier.make_regexes(bad_battles)

p1 = event_classifier.make_regex_string(event_classifier.easy_dance_keywords + event_classifier.dance_and_music_not_wrong_battle_keywords + event_classifier.easy_choreography_keywords)
p2 = event_classifier.make_regex_string(event_classifier.battle_keywords + event_classifier.n_x_n_keywords + event_classifier.contest_keywords)
dance_battles_regex = event_classifier.make_regexes([
    u'%s ?%s' % (p1, p2),
    u'%s ?%s' % (p2, p1),
])
assert dance_battles_regex[1].search('dance battle')
assert dance_battles_regex[1].search('custom breaking contest')
assert dance_battles_regex[1].search('concours choregraphique')

non_dance_support = [
    'fundraiser',
    'likes?',
    'votes?',
    'support',
]
non_dance_regex = event_classifier.make_regexes(non_dance_support)

# TODO: make sure this doesn't match... 'mc hiphop contest'

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

# TODO: accumulate reasons why we did/didn't accept. each event has a story
# TODO: also track "was a battle, but not sure about kind". good for maybe-queue.
# TODO: the above is useful for "ish" keywords, where if we know its a dance-event due to the magic bit, and it appears to be battle-ish-but-not-sure-about-dance-ish, then mark it battle-ish
# TOOD: in an effort to simplify, can we make a "battle-ish" bit be computed separately, and then try to figure out if it's dance-y after that using other keywords?
# TODO: If it has certain battle names in title, include automatically? redbull bc one cypher, etc

def is_battle(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')
    search_text = classified_event.final_search_text
    has_competitors = find_competitor_list(classified_event)
    if not has_competitors and classified_event.calc_inverse_keyword_density >= 5:
        return (False, 'relevant keywords too sparse')
    if not classified_event.real_dance_matches and not classified_event.manual_dance_keywords_matches:
        return (False, 'no strong dance keywords')

    no_bad_battles_search_text = bad_battles_regex[classified_event.boundaries].sub('', search_text)
    if dance_battles_regex[classified_event.boundaries].search(no_bad_battles_search_text):
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

