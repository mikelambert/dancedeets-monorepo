import re

from logic import event_classifier

def is_battle(classified_event):
    if not classified_event.is_dance_event():
        return (False, 'not a dance event')
    if not classified_event.real_dance_matches and not classified_event.manual_dance_keywords_matches:
        return (False, 'no strong dance keywords')
    search_text = classified_event.final_search_text
    if event_classifier.all_regexes['start_judge_keywords_regex'][classified_event.boundaries].search(search_text):
        if re.search('\b(?:dance battle|dance competition)\b', search_text):
            return (True, 'dance battle!')
        elif not re.search(r'\b(?:talent|beatbox|rap|beat battle|dj battle|swimsuit|graf(?:fiti)? battle|street fighter|tekken|capcom|games?|game breaking|videogames?|sexy|lingerie|sing|judge jules)\b', search_text):
            return (True, 'no ambiguous keywords')
        elif len(set(classified_event.real_dance_matches + classified_event.manual_dance_keywords_matches)) > 1:
            return (True, 'had some ambiguous keywords, but enough strong dance matches anyway')
        return (False, 'too ambiguous of a judge/jury result')
    return (False, 'no judge/jury')

