# -*-*- encoding: utf-8 -*-*-

import datetime
import re

from logic import event_classifier
from util import dates

# house side?
# lock side?
# experimental side?

# house battles http://www.dancedeets.com/events/admin_edit?event_id=240788332653377

house_keywords = [
    'house',
    'house dance',
]

connectors = [
    ' ?',
    ' di ',
    ' de ',
    ' ?: ?',
#    ' \W ',
]
connectors_regex = event_classifier.make_regex_string(connectors)

wrong_classes = [
    'on stage',
    'top class',
    'of course',
    'class\W?rnb',
    'class act',
    'breaking down',
    'ground\W?breaking',
    'main\Wstage',
    '(?:second|2nd) stage',
    'house classics?', # need to solve japanese case?
    'world\Wclass',
    'open house',
    'hip\W?hop\W?kempu?', # refers to hiphop music!
    'camp\W?house',
]

ambiguous_wrong_style_keywords = [
    'modern',
    'ballet',
    'ballroom',
]
p1 = event_classifier.make_regex_string(ambiguous_wrong_style_keywords)
p2 = event_classifier.make_regex_string(event_classifier.class_keywords)
wrong_classes += [
    u'%s%s%s' % (p1, connectors_regex, p2),
    u'%s%s%s' % (p2, connectors_regex, p1),
]
wrong_classes_regex = event_classifier.make_regexes(wrong_classes)

wrong_numbered_list = [
    'track(?:list(?:ing)?)?',
    'release',
    'download',
    'ep',
]
wrong_numbered_list_regex = event_classifier.make_regexes(wrong_numbered_list)

wrong_auditions = [
    'sing(?:ers?)?',
    'singing',
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
wrong_battles += [
    u'%s%s%s' % (p1, connectors_regex, p2),
    u'%s%s%s' % (p2, connectors_regex, p1), # this also gets "battle djs"
]
wrong_battles_regex = event_classifier.make_regexes(wrong_battles)


dance_class_styles = event_classifier.dance_and_music_not_wrong_battle_keywords + event_classifier.dance_keywords + house_keywords
dance_class_styles_regex = event_classifier.make_regexes(dance_class_styles)


cypher_regex = event_classifier.make_regex_string(event_classifier.cypher_keywords)
battle_regex = event_classifier.make_regex_string(event_classifier.battle_keywords)
p1_good = event_classifier.make_regex_string(dance_class_styles)
p1_okay = event_classifier.make_regex_string(event_classifier.easy_dance_keywords + event_classifier.easy_choreography_keywords)
p2_good = event_classifier.make_regex_string(event_classifier.battle_keywords + event_classifier.n_x_n_keywords + event_classifier.contest_keywords)
p2_okay = event_classifier.make_regex_string(event_classifier.easy_battle_keywords)
good_dance_battles_keywords = [
    u'%s%s%s' % (p1_good, connectors_regex, p2_good),
    u'%s%s%s' % (p2_good, connectors_regex, p1_good),
    'king of (?:the )?%s' % cypher_regex,
    '%s\W?king' % cypher_regex,
    'bonnie\s*(?:and|&)\s*clyde %s' % battle_regex,
    r'(?:seven|7)\W*(?:to|two|2)\W*(?:smoke|smook|somke)',
]
good_dance_battles_regex = event_classifier.make_regexes(good_dance_battles_keywords)

dance_battles_keywords = good_dance_battles_keywords + [
    u'%s%s%s' % (p1_okay, connectors_regex, p2_okay),
    u'%s%s%s' % (p2_okay, connectors_regex, p1_okay),
    u'%s%s%s' % (p1_okay, connectors_regex, p2_good),
    u'%s%s%s' % (p2_good, connectors_regex, p1_okay),
    u'%s%s%s' % (p1_good, connectors_regex, p2_okay),
    u'%s%s%s' % (p2_okay, connectors_regex, p1_good),
]
dance_battles_regex = event_classifier.make_regexes(dance_battles_keywords)
assert dance_battles_regex[1].search('dance battle')
assert dance_battles_regex[1].search('custom breaking contest')
assert dance_battles_regex[1].search('concours choregraphique')
assert dance_battles_regex[1].search('house dance battle')
assert good_dance_battles_regex[1].search('all-styles battle')
assert good_dance_battles_regex[1].search('custom breaking contest')

ambiguous_class_keywords = [
        'stage',
        'stages'
]
ambiguous_class_regex = event_classifier.make_regex_string(ambiguous_class_keywords)
p1 = event_classifier.make_regex_string(event_classifier.dance_and_music_not_wrong_battle_keywords + event_classifier.dance_keywords + house_keywords)
p2 = event_classifier.make_regex_string(event_classifier.class_keywords)
good_dance_class_regex = event_classifier.make_regexes([
    u'%s%s%s' % (p1, connectors_regex, p2),
    u'%s%s%s' % (p2, connectors_regex, p1),
    # only do one direction here, since we don't want "house stage" and "funk stage"
     u'%s%s%s' % (ambiguous_class_regex, connectors_regex, p1),
])
extended_class_regex = event_classifier.make_regexes(event_classifier.class_keywords + ambiguous_class_keywords)

non_dance_support = [
    'fundraiser',
    'likes?',
    'votes?',
    'support',
    'follow',
    '(?:pre)?sale',
]
non_dance_regex = event_classifier.make_regexes(non_dance_support)

full_judge_keywords = event_classifier.judge_keywords
judge_qualifier = event_classifier.make_regex_string(event_classifier.dance_keywords + event_classifier.easy_dance_keywords + event_classifier.dance_and_music_not_wrong_battle_keywords + house_keywords + event_classifier.easy_choreography_keywords + event_classifier.battle_keywords + event_classifier.n_x_n_keywords + event_classifier.contest_keywords)
judge_regex = event_classifier.make_regex_string(event_classifier.judge_keywords)
full_judge_keywords.extend([
        u'%s%s%s' % (judge_qualifier, connectors_regex, judge_regex),
        u'%s%s%s' % (judge_regex, connectors_regex, judge_qualifier),
])
start_judge_keywords_regex = event_classifier.make_regexes(full_judge_keywords, wrapper='^[^\w\n]*%s', flags=re.MULTILINE)

# TODO: make sure this doesn't match... 'mc hiphop contest'

vogue_keywords = [
    'butch realness',
    'butch queen',
    'vogue fem',
    'hand performance',
    'face performance',
    'femme queen',
    'sex siren',
    'vogue?ing',
    'voguin',
    'voguer[sz]?',
    'trans\W?man',
]
easy_vogue_keywords = [
    'never walked',
    'virgin',
    'drags?',
    'twist',
    'realness',
    'runway',
    'female figure',
    'couture',
    'butch',
    'ota',
    'open to all',
    'f\\.?q\\.?',
    'b\\.?q\\.?',
    'vogue',
    'house of',
    'category',
    'troph(?:y|ies)',
    'old way',
    'new way',
    'ball',
]
vogue_regex = event_classifier.make_regexes(vogue_keywords)
easy_vogue_regex = event_classifier.make_regexes(easy_vogue_keywords)

def has_list_of_good_classes(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')

    # if title is good strong keyword, and we have a list of classes:
    # why doesn't this get found by the is_workshop title classifier? where is our "camp" keyword
    # http://www.dancedeets.com/events/admin_edit?event_id=317006008387038

    #(?!20[01][05])
    time = r'\b[012]?\d[:.,h]?(?:[0-5][05])?(?:am|pm)?\b'
    time_with_minutes = r'\b[012]?\d[:.,h]?(?:[0-5][05])(?:am|pm)?\b'
    time_to_time = r'%s ?(?:to|do|до|til|till|a|-|[^\w,.]) ?%s' % (time, time)

    text = classified_event.search_text
    club_only_matches = event_classifier.all_regexes['club_only_regex'][classified_event.boundaries].findall(text)
    if len(club_only_matches) > 2:
        return False, 'too many club keywords: %s' % club_only_matches
    title_wrong_style_matches = event_classifier.all_regexes['dance_wrong_style_regex'][classified_event.boundaries].findall(classified_event.final_title)
    if title_wrong_style_matches:
        return False, 'wrong style in the title: %s' % title_wrong_style_matches
    lines = text.split('\n')
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

    for sub_lines in schedule_lines:
        good_lines = []
        if not [line for line in sub_lines if re.search(time_with_minutes, line)]:
            continue
        for line in sub_lines:
            dance_class_style_matches = event_classifier.all_regexes['dance_regex'][classified_event.boundaries].findall(line)
            dance_and_music_matches = event_classifier.all_regexes['dance_and_music_regex'][classified_event.boundaries].findall(line)
            manual_dancers = event_classifier.all_regexes['manual_dancers_regex'][classified_event.boundaries].findall(line)
            dance_wrong_style_matches = event_classifier.all_regexes['dance_wrong_style_title_regex'][classified_event.boundaries].findall(line)
            if (dance_class_style_matches or manual_dancers or dance_and_music_matches) and not dance_wrong_style_matches:
                good_lines.append(dance_class_style_matches + manual_dancers + dance_and_music_matches)
        start_time = dates.parse_fb_start_time(classified_event.fb_event)
        end_time = dates.parse_fb_end_time(classified_event.fb_event)
        if len(good_lines) > len(sub_lines) / 10 and (end_time.time() > datetime.time(12) or end_time - start_time > datetime.timedelta(hours=12)):
            return True, 'found good schedule: %s: %s' % ('\n'.join(sub_lines), good_lines)
    return False, ''

def find_competitor_list(classified_event):
    text = classified_event.search_text
    results = re.search(r'\n0*1[^\d].+\n^0*2[^\d].+\n(?:^\d+.+\n){2,}', text, re.MULTILINE)
    if results:
        numbered_list = results.group(0)
        num_lines = numbered_list.count('\n')
        if len(re.findall(r'\d ?[.:h] ?\d\d|am|pm', numbered_list)) > num_lines / 4:
            return False # good list of times! workshops, etc! performance/shows/club-set times!
        if len(event_classifier.all_regexes['event_regex'][classified_event.boundaries].findall(numbered_list)) > num_lines / 8:
            return False
        if wrong_numbered_list_regex[classified_event.boundaries].findall(text):
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

def is_battle(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')

    search_text = classified_event.final_search_text

    has_sparse_keywords = classified_event.calc_inverse_keyword_density >= 5
    has_competitors = find_competitor_list(classified_event)
    if not has_competitors and has_sparse_keywords:
        return (False, 'relevant keywords too sparse')
    
    no_wrong_battles_search_text = wrong_battles_regex[classified_event.boundaries].sub('', search_text)
    has_dance_battle = dance_battles_regex[classified_event.boundaries].findall(no_wrong_battles_search_text)
    has_good_dance_battle = good_dance_battles_regex[classified_event.boundaries].findall(no_wrong_battles_search_text)

    has_n_x_n = event_classifier.all_regexes['n_x_n_regex'][classified_event.boundaries].findall(search_text)
    has_battle = event_classifier.all_regexes['battle_regex'][classified_event.boundaries].findall(search_text)
    has_wrong_battle = wrong_battles_regex[classified_event.boundaries].findall(search_text)
    is_wrong_competition = non_dance_regex[classified_event.boundaries].findall(classified_event.final_title)
    is_wrong_style_battle_title = event_classifier.all_regexes['dance_wrong_style_title_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_many_real_dance_keywords = len(set(classified_event.real_dance_matches + classified_event.manual_dance_keywords_matches)) > 1
    has_start_judge = start_judge_keywords_regex[classified_event.boundaries].findall(search_text)

    if not has_good_dance_battle and not (classified_event.real_dance_matches or classified_event.manual_dance_keywords_matches):
        return (False, 'no strong dance keywords')

    if has_dance_battle and not is_wrong_competition and not is_wrong_style_battle_title and not has_wrong_battle:
        return (True, 'good-style real dance battle/comp! %s with keywords %s' % (has_dance_battle, (classified_event.real_dance_matches or classified_event.manual_dance_keywords_matches)))
    elif has_n_x_n and has_battle and not has_wrong_battle:
        return (True, 'battle keyword, NxN, good dance style')
    elif has_competitors and has_many_real_dance_keywords and not has_wrong_battle:
        return (True, 'has a list of competitors, and some strong dance keywords')
    elif has_start_judge and not has_wrong_battle:
        return (True, 'no ambiguous wrong-battle-style keywords')
    elif has_start_judge and has_many_real_dance_keywords:
        return (True, 'had some ambiguous keywords, but enough strong dance matches anyway')
    return (False, 'no judge/jury or battle/NxN')

def is_audition(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')

    has_audition = event_classifier.all_regexes['audition_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_good_dance_title = event_classifier.all_regexes['dance_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_extended_good_crew_title = event_classifier.all_regexes['extended_manual_dancers_regex'][classified_event.boundaries].findall(classified_event.final_title)


    search_text = classified_event.final_search_text
    has_good_dance = event_classifier.all_regexes['dance_regex'][classified_event.boundaries].findall(search_text)
    has_wrong_style = event_classifier.all_regexes['dance_wrong_style_title_regex'][classified_event.boundaries].findall(search_text)
    has_wrong_audition = wrong_auditions_regex[classified_event.boundaries].findall(search_text)

    if has_audition and (has_good_dance_title or has_extended_good_crew_title):
        return (True, 'has audition with strong title')
    if has_audition and has_good_dance and not has_wrong_style and not has_wrong_audition:
        return (True, 'has audition with good-and-not-bad dance style')
    return (False, 'no audition')

# Workshop examples to search for:
# - (Locking) 9.30am to 11.00am- 
# - (Popping) 11.15am to 12.45pm 

# - 16:30 - 17:30 - Maniek
# - 17:40 - 18:40 - Sandy
# - 18:50 - 19:50 - collabo Sandy & Maniek

# 14H00 – 15H30 DANCEHALL
# 15H30 – 17H00 HIP-HOP/NEWSTYLE
# 17H00 – 18H30 HOUSEDANCE
# 18H30 – 20H00 POPPING

# -------- 17:00 CLASE GRATUITA de House Dance con Crazy Toe 

# Sala 2 Danza Contemporanea Inter Atzewi Dance
# Company
# 17:30-18:50    Sala 1    Hip Hop princ Sacchetta Marcello+
# Raimondo
# Sala 2    Fusion inter     Antonio Fiore
# 19:00-20:20    Sala 1    Hip Hop Inter Sacchetta Marcello+     Raimondo

# = pondělí 19:15-20:45 – step
# = úterý 19:00-20:30 – street dance
# = úterý 19:00-20:00 – společenské tance pro páry
# = středa 19:00-20:30 – jazz dance

# Kyle Hanagami - Hip Hop
# Desiree Robbins - Jazz
# Alex Wong - Ballet/Jazz
# Mikey Trasoras - Hip Hop

# Di 5. Juni 2012 
# Performance Practice / Workshop Hip-Hop
# 
# Mi 6. Juni 2012 
# Performance Practice / Workshop BodyParkour / Performance im öffentlichen Raum / Österreich TANZT - Abend 1 / Österreich TANZT – Eröffnungsfest im Café Publik

# Commercial Dance 
# Úterky od 29.5. - 26.6. v 18:30-19:30 hod. (60 min.)

# LEECO & GIANINNI - SATURDAY, JUNE 16, 2012 @ 4:30PM
# somehow combined with bios below?

# SATURDAY July 14th, 2012
# 11:00 -12:25 Krumpin - Valerie Chartier 
# 12:30 - 1:55 House - JoJo Diggs
# 2:30 - 3:55 Dancehall - Neeks
# 4:00 - 5:30 Waacking - Cherry & Ebony

# Workshops KRUMP - BigFreezee (Royal Skillz, Cracow)
#
# Warsztaty Bboying - S-kel (Universal Zulu Nation )
#
# Workshops Street Dance - Prices (Royal Skillz)

# 1-2:30pm - Sexy Caribbean moves (Kay-Ann Ward)
# 2:30-4pm - Hip Hop Boot Camp


# 'dancehall workshop' in title should work as-is? why not?

# ALREADY CONFIRMED INSTRUCTORS!
# As of 06.14.12
# Subject to Change
# 
# Nika Kjlun
# Mr. Lucky


def is_workshop(classified_event):
    trimmed_title = wrong_classes_regex[classified_event.boundaries].sub('', classified_event.final_title)
    has_class_title = extended_class_regex[classified_event.boundaries].findall(trimmed_title)
    has_non_dance_event_title = non_dance_regex[classified_event.boundaries].findall(classified_event.final_title)
    has_good_dance_title = event_classifier.all_regexes['dance_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_extended_good_crew_title = event_classifier.all_regexes['extended_manual_dancers_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_wrong_style_title = event_classifier.all_regexes['dance_wrong_style_title_regex'][classified_event.boundaries].findall(classified_event.final_title)
    has_easy_dance_title = event_classifier.all_regexes['easy_dance_regex'][classified_event.boundaries].findall(classified_event.final_title)

    search_text = classified_event.final_search_text
    trimmed_search_text = wrong_classes_regex[classified_event.boundaries].sub('', search_text)
    has_good_dance_class = good_dance_class_regex[classified_event.boundaries].findall(trimmed_search_text)

    has_good_dance = event_classifier.all_regexes['dance_regex'][classified_event.boundaries].findall(trimmed_search_text)
    has_good_crew = event_classifier.all_regexes['manual_dancers_regex'][classified_event.boundaries].findall(trimmed_search_text)

    if has_class_title and (has_good_dance_title or has_extended_good_crew_title) and not has_wrong_style_title:
        return (True, 'has class with strong class-title: %s %s' % (has_class_title, (has_good_dance_title or has_extended_good_crew_title)))
    elif classified_event.is_dance_event() and has_good_dance_title and has_extended_good_crew_title and not has_wrong_style_title and not has_non_dance_event_title:
        return (True, 'has class with strong style-title: %s %s' % (has_good_dance_title, has_extended_good_crew_title))
    elif has_class_title and has_easy_dance_title and not has_wrong_style_title and (has_good_dance or has_good_crew):
        return (True, 'has dance class that contains strong description')
    elif has_good_dance_class and not has_wrong_style_title:
        return (True, 'has good dance class: %s' % has_good_dance_class)
    return (False, 'nothing')


def is_vogue_event(classified_event):
    text = classified_event.search_text
    vogue_matches = set(vogue_regex[classified_event.boundaries].findall(text))
    easy_vogue_matches = set(easy_vogue_regex[classified_event.boundaries].findall(text))
    match_count = len(vogue_matches) + 0.33 * len(easy_vogue_matches)
    if match_count > 2:
        return True, 'has vogue keywords: %s' % (vogue_matches.union(easy_vogue_matches))
    return False, 'not enough vogue keywords'

solo_lines_regex = None

def build_regexes():
    global solo_lines_regex

    if solo_lines_regex is not None:
        return

    solo_lines_regex = event_classifier.make_regexes(event_classifier.dance_keywords + event_classifier.manual_dancers, wrapper='^[^\w\n]*%s[^\w\n]*(?:$|\(|-)', flags=re.MULTILINE)

def has_standalone_keywords(classified_event):
    build_regexes()

    text = classified_event.search_text
    good_stuff_matches = solo_lines_regex[classified_event.boundaries].findall(text)
    # TODO(lambert): when doing set-building for uniqueness, try to get the matched text, not the stuff that prepends with non-word-chars
    if len(set(good_stuff_matches)) >= 2:
        return True, 'found good keywords on lines by themselves: %s' % good_stuff_matches
    return False, 'no good keywords on lines by themselves'

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
    result = has_list_of_good_classes(classified_event)
    if result[0]:
        return result
    result = is_vogue_event(classified_event)
    if result[0]:
        return result
    result = has_standalone_keywords(classified_event)
    if result[0]:
        return result
    return (False, 'nothing')

