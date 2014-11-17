# -*-*- encoding: utf-8 -*-*-
#

import re
import regex_keywords

# The magical repository of all dance keywords
_keywords = {}
_regex_strings = {}
_regexes = {}

def get_regex_string(token):
    if token in _regex_strings:
        return _regex_strings[token]
    else:
        _regex_strings[token] = regex_keywords.make_regex_string(_keywords[token])
        return _regex_strings[token]

def get_regex(token):
    if token in _regexes:
        return _regexes[token]
    else:
        # TODO(lambert): this is regexes, while function name is regex. We need to fix this (since make_regex is a different function)
        _regexes[token] = regex_keywords.make_regexes(_keywords[token])
        return _regexes[token]

def get(token):
    return _keywords[token]

def token(token_input):
    assert not re.match('\W', token_input)
    return '_%s_' % token_input

def add(token, keywords):
    # If anything has been built off of these, when we want to add new stuff, then we need to raise an error
    assert token not in _regexes
    assert token not in _regex_strings
    if token in _keywords:
        _keywords[token] += keywords
    else:
        _keywords[token] = keywords

# 'crew' biases dance one way, 'company' biases it another
EASY_DANCE = token('EASY_DANCE')
add(EASY_DANCE, [
    'dance style[sz]',
    'dances?', "dancin[g']?", 'dancers?',
    u'댄스', # korean dance
    u'댄서', # korean dancer
    u'танцы', # russian dancing
    u'танцоров', # russian dancers
    u'танцуват', # bulgarian dance
    u'танцува', # bulgarian dance
    u'танцовия', # bulgarian dance
    u'изтанцуват', # bulgarian dancing
    u'ダンサー', # japanese dance
    u'ダンス', # japanese dance
    u'춤.?', # korean dance
    u'추고.?.?', # korean dancing
    u'댄서.?.?', # korean dancers
    u'踊り', # japanese dance
    u'רוקד', # hebrew dance
    u'רקדם', # hebrew dancers
    u'רוקדים', # hebrew dance
    u'רקדנים', # hebrew dancers
    u'舞者', # chinese dancer
    u'舞技', # chinese dancing
    u'舞', # chinese dance
    u'舞蹈', # chinese dance
    u'排舞', # chinese dance
    u'แดนซ์', # dance thai
    u'เต้น', # dance thai
    u'กเต้น', # dancers thai
    'danse\w*', # french and danish
    'taniec', # dance polish
    u'tane?[cč][íú\w]*', # dance slovak/czech
    u'zatanč\w*', # dance czech
    u'tańe?c\w*', # dance polish/czech
    u'danç\w*', # dance portuguese
    'danza\w*', # dance italian
    u'šok\w*', # dance lithuanian
    'tanz\w*', # dance german
    'tanssi\w*', # finnish dance
    'bail[ae]\w*', # dance spanish
    'danzas', # dance spanish
    'ballerin[io]', # dancer italian
    'dansare', # dancers swedish
    'dansat', # dancing swedish
    'dansama', # dancers swedish
    'dansa\w*', # dance-* swedish
    'dansgolv', # dance floor swedish
    'dans', # swedish danish dance
    u'tänzern', # dancer german
    u'танчер', # dancer macedonian
    u'танцовиот', # dance macedonian
    'footwork',
    'plesa', # dance croatian
    'plesu', # dancing croatian
    u'nhảy', # dance vietnamese
    u'tänzer', # dancer german
])

EASY_CHOREO = token('EASY_CHOREO')
add(EASY_CHOREO, [
    u'(?:ch|k|c)oe?re[o|ó]?gra(?:ph|f)\w*', #english, italian, finnish, swedish, german, lithuanian, polish, italian, spanish, portuguese, danish
    'choreo',
    u'chorée', # french choreo
    u'chorégraph\w*', # french choreographer
    u'кореограф', # macedonian
])

GOOD_INSTANCE_OF_BAD_CLUB = token('GOOD_INSTANCE_OF_BAD_CLUB')
add(GOOD_INSTANCE_OF_BAD_CLUB, [
    'evelyn\W+champagne\W+king',
    'water\W?bottles?',
    'genie in (?:the|a) bottle',
])

BAD_CLUB = token('BAD_CLUB')
add(BAD_CLUB, [
    'bottle\W?service',
    'popping?\W?bottles?',
    'bottle\W?popping?',
    'bottles?',
    'grey goose',
    'champagne',
    'belvedere',
    'ciroc',
])

CYPHER = token('CYPHER')
add(CYPHER, [
    'c(?:y|i)ph(?:a|ers?)',
    u'サイファ', # japanese cypher
    u'サイファー', # japanese cypher
    u'サークル', # japanese circle
    u'サーク', # japanese circle
    'cerchi', # italian circle/cypher
    u'ไซเฟอร์', # thai cypher
    u'싸이퍼.?', # korean cypher
])

# if somehow has funks, hiphop, and breaks, and house. or 3/4? call it a dance event?

AMBIGUOUS_DANCE_MUSIC = token('AMBIGUOUS_DANCE_MUSIC')
add(AMBIGUOUS_DANCE_MUSIC, [
    'hip\W?hop',
    u'嘻哈', # chinese hiphop
    u'ההיפ הופ', # hebrew hiphop
    u'хипхоп', # macedonian hiphop
    u'ヒップホップ', # hiphop japanese
    u'힙합', # korean hiphop
    'hip\W?hop\w*', # lithuanian, polish hiphop
    'all\W?style[zs]?',
    'tou[ts]\W?style[zs]?', # french all-styles
    'tutti gli stili', # italian all-styles
    'be\W?bop',
    'shuffle',
    'swag',
    'funk',
    'dance\W?hall\w*',
    'ragga',
    'hype',
    'new\W?jack\W?swing',
    'gliding', 
    # 'breaks', # too many false positives
    'boogaloo',
    "breakin[g']?", 'breakers?',
    'jerk',
    'kpop',
    'rnb',
    "poppin\'?",
    'hard\Whitting',
    'electro\W?dance',
    'old\W?school hip\W?hop',
    '90\W?s hip\W?hop',
    'vogue',
    u'フリースタイル', # japanese freestyle
    'b\W?boy\w*', # 'bboyev' in slovak
])

# hiphop dance. hiphop dans?
DANCE = token('DANCE')
add(DANCE, [
    'street\W?jam',
    'breakingu', #breaking polish
    u'breaktánc', # breakdance hungarian
    u'ブレイク', # breakdance japanese
    'jazz rock',
    'funk\W?style[sz]?',
    'poppers?', 'popp?i?ng', # listing poppin in the ambiguous keywords
    'poppeurs?',
    'commercial hip\W?hop',
    'hip\W?hop dance',
    "jerk(?:ers?|in[g']?)",
    u'스트릿', # street korean
    u'ストリートダンス', # japanese streetdance
    u'街舞', # chinese streetdance / hiphop
    u'gatvės šokių', # lithuanian streetdance
    'katutanssi\w*', # finnish streetdance
    "bre?ak\W?dancin[g']?", 'bre?ak\W?dancer?s?',
    'break\W?danc\w+',
    'rock\W?dan[cs]\w+',
    '(?:lite|light)\W?feet',
    "gettin[g']?\W?(?:lite|light)",
    "turfin[g']?", 'turf danc\w+', "flexin[g']?", "buckin[g']?", "jookin[g']?",
    'b\W?boy[sz]?', "b\W?boyin[g']?", 'b\W?girl[sz]?', "b\W?girlin[g']?", 'power\W?moves?', "footworkin[g']?",
    u'파워무브', # powermove korean
    'breakeuse', # french bgirl
    'footworks', # spanish footworks
    "top\W?rock(?:s|er[sz]?|in[g']?)?", "up\W?rock(?:s|er[sz]?|in[g']?|)?",
    'houser[sz]?',
    'dance house', # seen in italian
    'soul dance',
    u'ソウルダンス', # soul dance japanese
    "lock(?:er[sz]?|in[g']?)?", 'lock dance',
    u'ロッカーズ', # japanese lockers
    u'ロッカ', # japanese lock
    "[uw]h?aa?c?c?k(?:er[sz]?|inn?[g']?)", # waacking
    "paa?nc?kin[g']?", # punking
    'locking4life',
    'dance crew[sz]?',
    "wavin[g']?", 'wavers?',
    'liquid\W+dance'
    'liquid\W+(?:\w+\W+)?digitz',
    'finger\W+digitz',
    'toy\W?man',
    'puppet\W?style',
    "bott?in[g']?",
    "robott?in[g']?",
    'melbourne shuffle',
    'strutter[sz]?', 'strutting',
    "tuttin[g']?", 'tutter[sz]?',
    'mj\W+style', 'michael jackson style',
    'mtv\W?style', 'mtv\W?dance', 'videoclip\w+', 'videodance',
    'hip\W?hop\Wheels',
    # only do la-style if not salsa? http://www.dancedeets.com/events/admin_edit?event_id=292605290807447
    # 'l\W?a\W?\Wstyle',
    'l\W?a\W?\Wdance',
    'n(?:ew|u)\W?style',
    'n(?:ew|u)\W?style\Whip\W?hop',
    'hip\W?hop\Wn(?:ew|u)\W?style',
    'mix(?:ed)?\W?style[sz]?', 'open\W?style[sz]',
    'all\W+open\W?style[sz]?',
    'open\W+all\W?style[sz]?',
    'me against the music',
    'krump', "krumpin[g']?", 'krumper[sz]?',
    'ragga\W?jamm?',
    'girl\W?s\W?hip\W?hop',
    'hip\W?hopp?er[sz]?',
    'street\W?jazz', 'street\W?funk',
    'jazz\W?funk', 'funk\W?jazz',
    'boom\W?crack',
    'hype danc\w*',
    'social hip\W?hop', 'hip\W?hop social dance[sz]', 'hip\W?hop party dance[sz]',
    'hip\W?hop grooves',
    '(?:new|nu|middle)\W?s(?:ch|k)ool\W\W?hip\W?hop', 'hip\W?hop\W\W?(?:old|new|nu|middle)\W?s(?:ch|k)ool',
    'newstyleurs?',
    'voguer[sz]?', "vogue?in[g']?", 'vogue fem', 'voguin',
    'vouge', "vougin[g']?",
    'fem queen', 'butch queen',
    'mini\W?ball', 'realness',
    'new\W?style hustle',
    'urban danc\w*',
    'urban style[sz]',
    'urban contemporary',
    u'dan[çc]\w* urban\w*',
    'dan\w+ urbai?n\w+', # spanish/french urban dance
    'baile urbai?n\w+', # spanish urban dance
    'estilo\w* urbai?n\w+', # spanish urban styles
    "pop\W{0,3}(?:(?:N|and|an)\W{1,3})?lock(?:in[g']?|er[sz]?)?",
])
# Crazy polish sometimes does lockingu and lockingy. Maybe we need to do this more generally though.
add(DANCE, [x+'u' for x in get(DANCE)])
# TODO(lambert): Is this a safe one to add?
# http://en.wikipedia.org/wiki/Slovak_declension
# dance_keywords = dance_keywords + [x+'y' for x in dance_keywords] 

# hiphop dance. hiphop dans?
HOUSE = token('HOUSE')
add(HOUSE, [
    'house',
    u'하우스', # korean house
    u'ハウス', # japanese house
    u'хаус', # russian house
])

#TODO(lambert): should these be done here, as additional keywords?
# Or should they be done as part oa grammar, that tries to combine these into larger tokens at that level

# freestyle dance
add(DANCE, ['%s ?%s' % (get_regex_string(HOUSE), get_regex_string(EASY_DANCE))])

FREESTYLE = token('FREESTYLE')
add(FREESTYLE, [
    'free\W?style(?:r?|rs?)',
])

STREET = token('STREET')
add(STREET, [
    'street',
])

add(DANCE, ['%s ?%s' % (get_regex_string(FREESTYLE), get_regex_string(EASY_DANCE))])
add(DANCE, [
  '%s ?%s' % (get_regex_string(AMBIGUOUS_DANCE_MUSIC), get_regex_string(EASY_DANCE)),
  '%s ?%s' % (get_regex_string(EASY_DANCE), get_regex_string(AMBIGUOUS_DANCE_MUSIC)),
])
add(DANCE, [
    '%s\W?%s\w*' % (get_regex_string(STREET), get_regex_string(EASY_CHOREO)),
    '%s\W?%s\w*' % (get_regex_string(STREET), get_regex_string(EASY_DANCE)),
])

