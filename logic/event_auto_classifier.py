import re

from logic import event_classifier

wrong_auditions = [
    'sing(?:ers?)?',
    'singer',
    'model',
    'poet(?:ry|s)?',
    'act(?:or|ress)?',
    'talent',
    'mike portoghese', # TODO(lambert): When we get bio removal for keyword matches, we can remove this one
]
wrong_auditions_regex = event_classifier.make_regexes(wrong_auditions)

wrong_battles = [
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
    'open mic',
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
wrong_battles.append(u'%s ?%s' % (p1, p2))
wrong_battles.append(u'%s ?%s' % (p1, p2))
wrong_battles_regex = event_classifier.make_regexes(wrong_battles)

p1 = event_classifier.make_regex_string(event_classifier.easy_dance_keywords + event_classifier.dance_and_music_not_wrong_battle_keywords + event_classifier.easy_choreography_keywords + event_classifier.dance_keywords)
p2 = event_classifier.make_regex_string(event_classifier.battle_keywords + event_classifier.n_x_n_keywords + event_classifier.contest_keywords + event_classifier.easy_battle_keywords)
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

full_judge_keywords = event_classifier.judge_keywords
judge_qualifier = event_classifier.make_regex_string(event_classifier.dance_keywords + event_classifier.easy_dance_keywords + event_classifier.dance_and_music_not_wrong_battle_keywords + event_classifier.easy_choreography_keywords + event_classifier.battle_keywords + event_classifier.n_x_n_keywords + event_classifier.contest_keywords)
judge_regex = event_classifier.make_regex_string(event_classifier.judge_keywords)
full_judge_keywords.extend([
        u'%s ?%s' % (judge_qualifier, judge_regex),
        u'%s ?%s' % (judge_regex, judge_qualifier),
])
start_judge_keywords_regex = event_classifier.make_regexes(full_judge_keywords, wrapper='^\W*%s', flags=re.MULTILINE)

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

def is_any_battle(classified_event):
    search_text = classified_event.final_search_text
    has_competitors = find_competitor_list(classified_event)
    has_start_judges = start_judge_keywords_regex[classified_event.boundaries].search(search_text)
    has_n_x_n_battle = (
        event_classifier.all_regexes['battle_regex'][classified_event.boundaries].search(search_text) and
        event_classifier.all_regexes['n_x_n_regex'][classified_event.boundaries].search(search_text)
    )
    no_wrong_battles_search_text = wrong_battles_regex[classified_event.boundaries].sub('', search_text)
    has_dance_battle = (
        dance_battles_regex[classified_event.boundaries].search(no_wrong_battles_search_text) and
        non_dance_regex[classified_event.boundaries].search(classified_event.final_title)
    )
    return has_competitors or has_start_judges or has_n_x_n_battle or has_dance_battle

def is_real_dance(classified_event):
    search_text = classified_event.final_search_text
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')


def is_battle(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')

    search_text = classified_event.final_search_text
    if not classified_event.real_dance_matches and not classified_event.manual_dance_keywords_matches:
        return (False, 'no strong dance keywords')

    has_sparse_keywords = classified_event.calc_inverse_keyword_density >= 5
    has_competitors = find_competitor_list(classified_event)
    if not has_competitors and has_sparse_keywords:
        return (False, 'relevant keywords too sparse')
    
    no_wrong_battles_search_text = wrong_battles_regex[classified_event.boundaries].sub('', search_text)
    has_dance_battle = dance_battles_regex[classified_event.boundaries].findall(no_wrong_battles_search_text)

    has_n_x_n_battle = event_classifier.all_regexes['n_x_n_regex'][classified_event.boundaries].findall(search_text)
    has_battle = event_classifier.all_regexes['battle_regex'][classified_event.boundaries].findall(search_text)
    has_wrong_battle = wrong_battles_regex[classified_event.boundaries].findall(search_text)
    is_wrong_competition = non_dance_regex[classified_event.boundaries].findall(classified_event.final_title)
    is_wrong_style_battle = event_classifier.all_regexes['dance_wrong_style_title_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_many_real_dance_keywords = len(set(classified_event.real_dance_matches + classified_event.manual_dance_keywords_matches)) > 1
    has_start_judge = start_judge_keywords_regex[classified_event.boundaries].findall(search_text)

    # has_real_dance_battle? where is 'locking battle' in all of this? in our check for real_dance_matches combined with the others?

    if has_dance_battle and not is_wrong_competition and not is_wrong_style_battle:
        return (True, 'good-style real dance battle/comp!')
    if has_n_x_n_battle and has_battle and not has_wrong_battle:
        return (True, 'battle keyword, NxN, good dance style')
    if has_competitors and has_many_real_dance_keywords and not has_wrong_battle:
        return (True, 'has a list of competitors, and some strong dance keywords')
    if has_start_judge and not has_wrong_battle:
        return (True, 'no ambiguous wrong-battle-style keywords')
    if has_start_judge and has_many_real_dance_keywords:
        return (True, 'had some ambiguous keywords, but enough strong dance matches anyway')
    return (False, 'no judge/jury or battle/NxN')

def is_audition(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')

    has_audition = event_classifier.all_regexes['audition_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_good_dance_title = event_classifier.all_regexes['dance_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_good_crew_title = event_classifier.all_regexes['extended_manual_dance_keywords_regex'][classified_event.boundaries].findall(classified_event.final_title)


    search_text = classified_event.final_search_text
    has_good_dance = event_classifier.all_regexes['dance_regex'][classified_event.boundaries].findall(search_text)
    has_wrong_style = event_classifier.all_regexes['dance_wrong_style_title_regex'][classified_event.boundaries].findall(search_text)
    has_wrong_audition = wrong_auditions_regex[classified_event.boundaries].findall(search_text)

    if has_audition and (has_good_dance_title or has_good_crew_title):
        return (True, 'has audition with strong title')
    if has_audition and has_good_dance and not has_wrong_style and not has_wrong_audition:
        return (True, 'has audition with good-and-not-bad dance style')
    return (False, 'no audition')

def is_workshop(classified_event):
    has_class = event_classifier.all_regexes['class_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_good_dance_title = event_classifier.all_regexes['dance_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_good_crew_title = event_classifier.all_regexes['manual_dance_keywords_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_wrong_style_title = event_classifier.all_regexes['dance_wrong_style_title_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_easy_dance_title = event_classifier.all_regexes['easy_dance_regex'][classified_event.boundaries].findall(classified_event.final_title)

    search_text = classified_event.final_search_text
    has_good_dance = event_classifier.all_regexes['dance_regex'][classified_event.boundaries].findall(search_text)
    has_good_crew = event_classifier.all_regexes['manual_dance_keywords_regex'][classified_event.boundaries].findall(search_text)

    if has_class and (has_good_dance_title or has_good_crew_title) and not has_wrong_style_title:
        return (True, 'has class with strong title')

    elif has_class and has_easy_dance_title and not has_wrong_style_title and (has_good_dance or has_good_crew):
        return (True, 'has dance class that contains strong description')
    return (False, 'nothing')

def is_auto_add_event(classified_event):
    result = is_battle(classified_event)
    if result[0]:
        return result
    result = is_audition(classified_event)
    if result[0]:
        return result
    result = is_workshop(classified_event)
    if result[0]:
        return result
    return (False, 'nothing')

