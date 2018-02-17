# -*-*- encoding: utf-8 -*-*-

import datetime
import logging
try:
    import re2
    import re2 as re
except ImportError as e:
    logging.info("Could not import re2, falling back to re: %s", e)
    re2 = None
    import re

from dancedeets import event_types
from .. import categories
from .. import event_classifier
from .. import event_structure
from .. import grammar
from . import keywords
from . import rules


def is_street_event(classified_event):
    result = _is_street_event(classified_event)
    return result[0], [result[1]], result[2]


def _is_street_event(classified_event):
    good_bad_pairings = [
        (keywords.STYLE_HOUSE, keywords.WRONG_HOUSE),
        (keywords.STYLE_BREAK, keywords.WRONG_BREAK),
        (keywords.STYLE_LOCK, keywords.WRONG_LOCK),
        (keywords.STYLE_FLEX, keywords.WRONG_FLEX),
        (grammar.Any(keywords.STYLE_POP, 'pop'), keywords.WRONG_POP),
    ]
    for good, bad in good_bad_pairings:
        if classified_event.processed_text.has_token(good) and classified_event.processed_text.has_token(bad):
            return (False, 'has bad-token for equivalent good-token, skipping', None)

    result = is_intentional(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET
    result = is_battle(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET
    result = is_audition(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET
    result = is_workshop(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET
    result = has_list_of_good_classes(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET
    result = is_vogue_event(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET
    result = has_standalone_keywords(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET
    result = has_good_event_title(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET
    result = is_performance_or_practice(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET
    result = has_many_street_styles(classified_event)
    if result[0]:
        return result[0], result[1], event_types.VERTICALS.STREET

    return result[0], result[1], event_types.VERTICALS.STREET


def has_many_street_styles(classified_event):
    title_wrong_style_matches = classified_event.processed_title.has_token(keywords.DANCE_WRONG_STYLE)
    if title_wrong_style_matches:
        return False, 'wrong style in the title: %s' % title_wrong_style_matches

    styles = categories.find_styles_strict(classified_event)
    et = categories.find_event_types(classified_event)
    music_only = classified_event.processed_text.get_tokens(keywords.MUSIC_ONLY)
    # If they mention too many other styles of music, then our dance styles were probably just referring to music
    # If they are at a party, then it's also probably referring to music
    # Instead we're left with classes, camps, battles, shows, etc that showcase real dance styles
    if len(music_only) <= 1 and len(styles) >= 4 and event_types.PARTY not in et:
        styles = [x.public_name for x in styles]
        et = [x.public_name for x in et]
        return (True, 'Found enough street styles: %s: %s, with music: %s' % (et, styles, music_only))
    return False, ''


# house side?
# lock side?
# experimental side?
# TODO: make sure this doesn't match... 'mc hiphop contest'


def has_list_of_good_classes(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')

    start_time = classified_event.start_time
    end_time = classified_event.end_time
    # Ignore club events (ends in the morning and less than 12 hours long)
    if end_time and end_time.time() < datetime.time(12) and end_time - start_time < datetime.timedelta(hours=12):
        return False, 'end time indicates club event'

    club_only_matches = classified_event.processed_text.get_tokens(keywords.CLUB_ONLY)
    if len(club_only_matches) > 2:
        return False, 'too many club keywords: %s' % club_only_matches
    title_wrong_style_matches = classified_event.processed_title.has_token(keywords.DANCE_WRONG_STYLE)
    if title_wrong_style_matches:
        return False, 'wrong style in the title: %s' % title_wrong_style_matches

    # if title is good strong keyword, and we have a list of classes:
    # why doesn't this get found by the is_workshop title classifier? where is our "camp" keyword
    # https://www.dancedeets.com/events/admin_edit?event_id=317006008387038

    schedule_groups = event_structure.get_schedule_line_groups(classified_event)
    for schedule_lines in schedule_groups:
        good_lines = []
        for line in schedule_lines:
            proc_line = event_classifier.StringProcessor(line, classified_event.boundaries)
            proc_line.tokenize(keywords.AMBIGUOUS_DANCE_MUSIC)
            dance_class_style_matches = proc_line.get_tokens(rules.GOOD_DANCE)
            dance_and_music_matches = proc_line.get_tokens(keywords.AMBIGUOUS_DANCE_MUSIC)
            manual_dancers = proc_line.get_tokens(rules.MANUAL_DANCER[grammar.STRONG])
            dance_wrong_style_matches = proc_line.has_token(rules.DANCE_WRONG_STYLE_TITLE)

            # Sometimes we have a schedule with hiphop and ballet
            # Sometimes we have a schedule with hiphop and dj and beatbox/rap (more on music side)
            # Sometimes we have a schedule with hiphop, house, and beatbox (legit, crosses boundaries)
            # TODO: Should do a better job of classifying the ambiguous music/dance types, based on the presence of non-ambiguous dance types too
            if (dance_class_style_matches or manual_dancers or dance_and_music_matches) and not dance_wrong_style_matches:
                good_lines.append(dance_class_style_matches + manual_dancers + dance_and_music_matches)
        if len(good_lines) > len(schedule_lines) / 10:
            return True, 'found good schedule: %s: %s' % ('\n'.join(schedule_lines), good_lines)
    return False, ''


# TODO: accumulate reasons why we did/didn't accept. each event has a story
# TODO: also track "was a battle, but not sure about kind". good for maybe-queue.
# TODO: the above is useful for "ish" keywords, where if we know its a dance-event due to the magic bit, and it appears to be battle-ish-but-not-sure-about-dance-ish, then mark it battle-ish
# TODO: in an effort to simplify, can we make a "battle-ish" bit be computed separately, and then try to figure out if it's dance-y after that using other keywords?
# TODO: If it has certain battle names in title, include automatically? redbull bc one cypher, etc


# TODO: UNUSED!
def is_any_battle(classified_event):
    has_competitors = event_structure.find_competitor_list(classified_event.search_text)
    has_start_judges = classified_event.processed_text.has_token(rules.START_JUDGE)
    has_n_x_n_battle = (
        classified_event.processed_text.has_token(keywords.BATTLE) and classified_event.processed_text.has_token(keywords.N_X_N)
    )
    no_wrong_battles_processed = classified_event.processed_text.delete_with_rule(rules.WRONG_BATTLE)
    has_dance_battle = (
        no_wrong_battles_processed.has_token(rules.DANCE_BATTLE) and
        not classified_event.processed_title.has_token(keywords.BAD_COMPETITION_TITLE_ONLY)
    )
    return has_competitors or has_start_judges or has_n_x_n_battle or has_dance_battle


def is_battle(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')

    has_sparse_keywords = classified_event.calc_inverse_keyword_density >= 5.2
    has_competitors = event_structure.find_competitor_list(classified_event.search_text)
    # print has_competitors, has_sparse_keywords, classified_event.calc_inverse_keyword_density
    if not has_competitors and has_sparse_keywords:
        return (False, 'relevant keywords too sparse')

    no_wrong_battles_processed = classified_event.processed_text.delete_with_rule(rules.WRONG_BATTLE)
    has_dance_battle = no_wrong_battles_processed.has_token(rules.DANCE_BATTLE)
    has_good_dance_battle = no_wrong_battles_processed.has_token(rules.GOOD_DANCE_BATTLE)

    has_n_x_n = classified_event.processed_text.has_token(keywords.N_X_N)
    has_battle = classified_event.processed_text.has_token(keywords.BATTLE)
    has_wrong_battle = classified_event.processed_text.has_token(rules.WRONG_BATTLE)
    is_wrong_competition_title = classified_event.processed_title.has_token(keywords.BAD_COMPETITION_TITLE_ONLY)
    is_wrong_style_battle_title = classified_event.processed_title.has_token(rules.DANCE_WRONG_STYLE_TITLE)
    has_many_real_dance_keywords = len(set(classified_event.real_dance_matches + classified_event.manual_dance_keywords_matches)) > 1
    has_start_judge = classified_event.processed_text.has_token(rules.START_JUDGE)

    # print has_dance_battle
    # print is_wrong_competition_title
    # print is_wrong_style_battle_title
    # print has_wrong_battle
    # print has_good_dance_battle
    # print classified_event.real_dance_matches
    # print classified_event.manual_dance_keywords_matches
    # print classified_event.processed_text.get_tokenized_text().encode('utf8')
    # print classified_event.processed_text.match_on_word_boundaries
    # print has_start_judge
    # print classified_event.real_dance_matches + classified_event.manual_dance_keywords_matches
    # print has_many_real_dance_keywords
    if not has_good_dance_battle and not (classified_event.real_dance_matches or classified_event.manual_dance_keywords_matches):
        return (False, 'no strong dance keywords')

    if has_good_dance_battle and not is_wrong_competition_title and not is_wrong_style_battle_title:
        return (True, 'real dance-style battle/comp! %s' % has_good_dance_battle)
    elif has_dance_battle and not is_wrong_competition_title and not is_wrong_style_battle_title and not has_wrong_battle:
        return (
            True, 'good-style real dance battle/comp! %r with keywords %s' %
            (has_dance_battle, (classified_event.real_dance_matches or classified_event.manual_dance_keywords_matches))
        )
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

    has_audition = classified_event.processed_title.has_token(keywords.AUDITION)
    has_good_dance_title = classified_event.processed_title.has_token(rules.GOOD_DANCE)
    has_extended_good_crew_title = classified_event.processed_title.has_token(rules.MANUAL_DANCER[grammar.STRONG_WEAK])

    has_good_dance = classified_event.processed_text.has_token(rules.GOOD_DANCE)
    has_wrong_style = classified_event.processed_text.has_token(rules.DANCE_WRONG_STYLE_TITLE)
    has_wrong_audition = classified_event.processed_text.has_token(keywords.WRONG_AUDITION)

    if has_audition and (has_good_dance_title or has_extended_good_crew_title):
        return (True, 'has audition with strong title')
    elif has_audition and has_good_dance and not has_wrong_style and not has_wrong_audition:
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
    trimmed_title = classified_event.processed_title.delete_with_rule(rules.WRONG_CLASS)
    if classified_event.processed_text.get_tokens(keywords.ROMANCE):
        has_class_title = trimmed_title.get_tokens(rules.ROMANCE_EXTENDED_CLASS_ONLY)
    else:
        has_class_title = trimmed_title.get_tokens(keywords.CLASS_ONLY)
    has_good_dance_class_title = trimmed_title.has_token(rules.GOOD_DANCE_CLASS)

    has_non_dance_event_title = classified_event.processed_title.has_token(keywords.BAD_COMPETITION_TITLE_ONLY)
    has_good_dance_title = trimmed_title.has_token(rules.GOOD_DANCE)
    has_extended_good_crew_title = trimmed_title.has_token(rules.MANUAL_DANCER[grammar.STRONG_WEAK])

    has_wrong_style_title = classified_event.processed_title.has_token(rules.DANCE_WRONG_STYLE_TITLE)

    lee_lee_hiphop = 'lee lee' in classified_event.final_title and re.findall('hip\W?hop', classified_event.final_title)

    trimmed_text = classified_event.processed_text.delete_with_rule(rules.WRONG_CLASS)
    has_good_dance_class = trimmed_text.has_token(rules.GOOD_DANCE_CLASS)
    has_good_dance = classified_event.processed_text.has_token(rules.GOOD_DANCE)
    has_wrong_style = classified_event.processed_text.has_token(rules.DANCE_WRONG_STYLE_TITLE)

    has_good_crew = classified_event.processed_text.has_token(rules.MANUAL_DANCER[grammar.STRONG])

    # print has_class_title
    # print has_good_dance_title
    # print has_extended_good_crew_title
    # print has_wrong_style_title

    # print classified_event.final_search_text
    # print classified_event.processed_text.get_tokenized_text()
    # print ''
    # print has_class_title
    # print has_wrong_style
    # print has_good_dance
    # print has_good_crew
    if has_class_title and (has_good_dance_title or has_extended_good_crew_title) and not has_wrong_style_title:
        return (
            True, 'has class with strong class-title: %s %s' % (has_class_title, (has_good_dance_title or has_extended_good_crew_title))
        )
    elif classified_event.is_dance_event(
    ) and has_good_dance_title and has_extended_good_crew_title and not has_wrong_style_title and not has_non_dance_event_title:
        return (True, 'has class with strong style-title: %s %s' % (has_good_dance_title, has_extended_good_crew_title))
    elif classified_event.is_dance_event() and lee_lee_hiphop and not has_wrong_style_title and not has_non_dance_event_title:
        return (True, 'has class with strong style-title: %s %s' % (has_good_dance_title, has_extended_good_crew_title))
    elif has_class_title and not has_wrong_style and (has_good_dance or has_good_crew):
        return (True, 'has class title: %s, that contains strong description %s, %s' % (has_class_title, has_good_dance, has_good_crew))
    elif has_good_dance_class_title:
        return (True, 'has good dance class title: %s' % has_good_dance_class_title)
    elif has_good_dance_class and not has_wrong_style_title:
        return (True, 'has good dance class: %s' % has_good_dance_class)
    return (False, 'nothing')


def is_vogue_event(classified_event):
    # We use sets here to get unique keywords
    vogue_matches = set(classified_event.processed_text.get_tokens(keywords.VOGUE))
    easy_vogue_matches = set(classified_event.processed_text.get_tokens(keywords.EASY_VOGUE, keywords.TOO_EASY_VOGUE))
    match_count = len(vogue_matches) + 0.34 * len(easy_vogue_matches)
    # print vogue_matches, easy_vogue_matches, match_count
    if match_count > 2:
        return True, 'has vogue keywords: %s' % (vogue_matches.union(easy_vogue_matches))
    return False, 'not enough vogue keywords'


def has_standalone_keywords(classified_event):
    solo_lines_regex = rules.GOOD_SOLO_LINE.hack_double_regex()[classified_event.boundaries]
    text = classified_event.search_text
    good_matches = set()
    for line in text.split('\n'):
        alpha_line = re.sub(r'\W+', '', line)
        if not alpha_line:
            continue
        remaining_line = solo_lines_regex.sub('', line)
        deleted_length = len(line) - len(remaining_line)
        if 0.5 < 1.0 * deleted_length / len(alpha_line):
            good_matches.add(solo_lines_regex.findall(line)[0])  # at most one keyword per line
    if len(good_matches) >= 2:
        return True, 'found good keywords on lines by themselves: %s' % set(good_matches)
    return False, 'no good keywords on lines by themselves'


def has_good_event_title(classified_event):
    non_dance_title_keywords = classified_event.processed_title.has_token(keywords.BAD_COMPETITION_TITLE_ONLY)
    wrong_battles_title = classified_event.processed_title.has_token(rules.WRONG_BATTLE)
    title_keywords = classified_event.processed_title.has_token(keywords.COMPETITION[grammar.STRONG])
    if title_keywords and not non_dance_title_keywords and not wrong_battles_title:
        return True, 'looks like a good event title: %s' % title_keywords
    return False, 'no good event title'


def has_good_djs_title(classified_event):
    non_dance_title_keywords = classified_event.processed_title.has_token(keywords.BAD_COMPETITION_TITLE_ONLY)
    wrong_battles_title = classified_event.processed_title.has_token(rules.WRONG_BATTLE)
    title_keywords = classified_event.processed_title.has_token(keywords.GOOD_DJ)

    if title_keywords and not non_dance_title_keywords and not wrong_battles_title:
        return True, 'looks like a good dj title: %s' % title_keywords
    return False, 'no good dj title'


def is_performance_or_practice(classified_event):
    performances_and_practices = classified_event.processed_short_lines.has_token(rules.PERFORMANCE_PRACTICE)
    if performances_and_practices:
        return True, 'found good performance/practice keywords: %s' % performances_and_practices
    return False, 'no good keywords'


def is_intentional(classified_event):
    if 'dancedeets' in classified_event.final_search_text:
        return True, 'found dancedeets reference'
    return False, 'no dancedeets reference'


def is_bad_club(classified_event):
    has_battles = classified_event.processed_text.has_token(rules.DANCE_BATTLE)
    has_style = classified_event.processed_text.has_token(rules.GOOD_DANCE)
    has_manual_keywords = classified_event.processed_text.has_token(rules.MANUAL_DANCE[grammar.STRONG_WEAK])
    has_cypher = classified_event.processed_text.count_tokens(keywords.CYPHER)

    has_other_event_title = classified_event.processed_title.has_token(keywords.EVENT)

    has_ambiguous_text = has_battles or has_style or has_manual_keywords or has_cypher
    if classified_event.processed_text.count_tokens(keywords.BAD_CLUB) and not has_ambiguous_text and not has_other_event_title:
        return True, 'has bad keywords: %s' % classified_event.processed_text.get_tokens(keywords.BAD_CLUB)
    return False, 'not a bad club'


def is_bad_wrong_dance(classified_event):
    dance_and_music_matches = classified_event.processed_text.get_tokens(keywords.AMBIGUOUS_DANCE_MUSIC)
    real_dance_keywords = set(classified_event.real_dance_matches + dance_and_music_matches)
    manual_keywords = classified_event.manual_dance_keywords_matches

    nodance_processed_text = event_classifier.StringProcessor(classified_event.search_text, classified_event.boundaries)
    nodance_processed_text.real_tokenize(rules.MANUAL_DANCE[grammar.STRONG])
    nodance_processed_text.real_tokenize(rules.GOOD_DANCE)
    weak_classical_dance_keywords = nodance_processed_text.get_tokens(keywords.SEMI_BAD_DANCE)
    strong_classical_dance_keywords = nodance_processed_text.get_tokens(rules.DANCE_WRONG_STYLE_TITLE)

    has_house = classified_event.processed_text.has_token(keywords.HOUSE)
    club_only_matches = classified_event.processed_text.get_tokens(keywords.CLUB_ONLY)

    keyword_count = len(strong_classical_dance_keywords) + 0.5 * len(weak_classical_dance_keywords)

    just_free_style_dance = len(real_dance_keywords) == 1 and list(real_dance_keywords)[0].startswith('free')

    has_wrong_style_title = classified_event.processed_title.get_tokens(rules.DANCE_WRONG_STYLE_TITLE)
    has_decent_style = classified_event.processed_title.get_tokens(rules.DECENT_DANCE)
    if has_wrong_style_title and not has_decent_style:
        return True, 'Title is too strong a negative, without any compensating good title keywords'
    elif not real_dance_keywords and not has_house and len(club_only_matches) <= 1 and len(manual_keywords) <= 1 and keyword_count >= 2:
        return True, 'Has strong classical keywords %s, but only real keywords %s' % (
            strong_classical_dance_keywords + weak_classical_dance_keywords, manual_keywords
        )
    elif keyword_count >= 2 and just_free_style_dance and not manual_keywords:
        return True, 'Has strong classical keywords %s with freestyle dance, but only dance keywords %s' % (
            strong_classical_dance_keywords + weak_classical_dance_keywords, real_dance_keywords.union(manual_keywords)
        )
    return False, 'not a bad classical dance event'
