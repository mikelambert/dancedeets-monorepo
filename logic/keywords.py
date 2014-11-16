# -*-*- encoding: utf-8 -*-*-
#

import re
import regex_keywords

# The magical repository of all dance keywords
_keywords = {}

def get(token):
    return _keywords[token]

def token(token_input):
    assert not re.match('\W', token_input)
    return '_%s_' % token_input

# 'crew' biases dance one way, 'company' biases it another
EASY_DANCE = token('EASY_DANCE')
_keywords[EASY_DANCE] = [
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
]

EASY_CHOREO = token('EASY_CHOREO')
_keywords[EASY_CHOREO] = [
    u'(?:ch|k|c)oe?re[o|ó]?gra(?:ph|f)\w*', #english, italian, finnish, swedish, german, lithuanian, polish, italian, spanish, portuguese, danish
    'choreo',
    u'chorée', # french choreo
    u'chorégraph\w*', # french choreographer
    u'кореограф', # macedonian
]

GOOD_INSTANCE_OF_BAD_CLUB = token('GOOD_INSTANCE_OF_BAD_CLUB')
_keywords[GOOD_INSTANCE_OF_BAD_CLUB] = [
    'evelyn\W+champagne\W+king',
    'water\W?bottles?',
    'genie in (?:the|a) bottle',
]

BAD_CLUB = token('BAD_CLUB')
_keywords[BAD_CLUB] = [
    'bottle\W?service',
    'popping?\W?bottles?',
    'bottle\W?popping?',
    'bottles?',
    'grey goose',
    'champagne',
    'belvedere',
    'ciroc',
]

CYPHER = token('CYPHER')
_keywords[CYPHER] = [
    'c(?:y|i)ph(?:a|ers?)',
    u'サイファ', # japanese cypher
    u'サイファー', # japanese cypher
    u'サークル', # japanese circle
    u'サーク', # japanese circle
    'cerchi', # italian circle/cypher
    u'ไซเฟอร์', # thai cypher
    u'싸이퍼.?', # korean cypher
]

regexes = dict((token, regex_keywords.make_regexes(keywords)) for (token, keywords) in _keywords.iteritems())

def get_regex(token):
    return regexes[token]
