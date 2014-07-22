# -*-*- encoding: utf-8 -*-*-

import codecs
import logging
import math
try:
    import re2
    import re2 as re
except ImportError:
    logging.info("Could not import re2, falling back to re.")
    re2 = None
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)
import time
from util import re_flatten
from util import cjk_detect
from spitfire.runtime.filters import skip_filter

USE_UNICODE = False

# TODO: translate to english before we try to apply the keyword matches
# TODO: if event creator has created dance events previously, give it some weight
# TODO: 

# TODO: for each style-keyword, give it some weight. don't be a requirement but yet-another-bayes-input
# TODO: add a bunch of classifier logic
# TODO: for iffy events, assume @ in the title means its a club event. same with monday(s) tuesday(s) etc.
# TODO: house class, house workshop, etc, etc. since 'house' by itself isn't sufficient
# maybe feed keywords into auto-classifying event type? bleh.

def make_regex_string(strings, matching=False, word_boundaries=False, match_cjk=False, wrapper='%s'):
    inner_regex = re_flatten.construct_regex(strings)
    if matching:
        regex = u'(' + inner_regex + u')'
    else:
        regex = u'(?:' + inner_regex + u')'
    if word_boundaries:
        if match_cjk:
            regex = '(?u)%s' % regex
        else:
            regex = r'\b%s\b' % regex
    regex = wrapper % regex
    return regex


# 'crew' biases dance one way, 'company' biases it another
easy_dance_keywords = [
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
easy_choreography_keywords = [
    u'(?:ch|k|c)oe?re[o|ó]?gra(?:ph|f)\w*', #english, italian, finnish, swedish, german, lithuanian, polish, italian, spanish, portuguese, danish
    'choreo',
    u'chorée', # french choreo
    u'chorégraph\w*', # french choreographer
    u'кореограф', # macedonian
]

# if somehow has funks, hiphop, and breaks, and house. or 3/4? call it a dance event?

dance_and_music_keywords = [
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
]

# hiphop dance. hiphop dans?
dance_keywords = [
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
]
# Crazy polish sometimes does lockingu and lockingy. Maybe we need to do this more generally though.
dance_keywords = dance_keywords + [x+'u' for x in dance_keywords] 
# TODO(lambert): Is this a safe one to add?
# http://en.wikipedia.org/wiki/Slovak_declension
# dance_keywords = dance_keywords + [x+'y' for x in dance_keywords] 

house_keywords = [
    'house',
    u'하우스', # korean house
    u'ハウス', # japanese house
    u'хаус', # russian house
]
house_regex_string = make_regex_string(house_keywords)

# freestyle dance
easy_dance_regexes = make_regex_string(easy_dance_keywords)
dance_keywords += ['%s ?%s' % (house_regex_string, easy_dance_regexes)]

dance_keywords += ['free\W?style(?:r?|rs?) ?%s' % easy_dance_regexes]
dance_and_music_regexes = make_regex_string(dance_and_music_keywords)
dance_keywords += [
  '%s ?%s' % (dance_and_music_regexes, easy_dance_regexes),
  '%s ?%s' % (easy_dance_regexes, dance_and_music_regexes),
]
dance_keywords += [
    'street\W?%s\w*' % make_regex_string(easy_choreography_keywords),
    'street\W?%s\w*' % make_regex_string(easy_dance_keywords),
]


easy_battle_keywords = [
    'jams?', 
]
easy_event_keywords = [
    'club', 'after\Wparty', 'pre\Wparty',
    u'クラブ',  # japanese club
    'open sessions?',
    'training',
]
easy_event_keywords += easy_battle_keywords
contest_keywords = [
    'contests?',
    'concours', # french contest
    'konkurrencer', # danish contest
    'dancecontests', # dance contests german
]
practice_keywords = [
    'sesja', # polish session
    'sessions', 'practice',
]
performance_keywords = [
    # international sessions are handled down below
    'shows?', 'performances?',
    'show\W?case',
    u'représentation', # french performance
    u'ショーケース', # japanese showcase
    u'秀', # chinese show
    u'的表演', # chinese performance
    u'表演', # chinese performance
    u'vystoupení', # czech performances
    u'výkonnostních', # czech performance
    u'изпълнението', # bulgarian performance
    u'パフォーマンス', # japanese performance
    # maybe include 'spectacle' as well?
    'esibizioni', #italian performance/exhibition
]

club_and_event_keywords = practice_keywords + performance_keywords + contest_keywords

club_only_keywords = [
    'club',
    'bottle service',
    'table service',
    'coat check',
    #'rsvp',
    'free before',
    #'dance floor',
    #'bar',
    #'live',
    #'and up',
    'vip',
    'guest\W?list',
    'drink specials?',
    'resident dj\W?s?',
    'residency',
    'ravers?',
    'dj\W?s?',
    'techno', 'trance', 'indie', 'glitch',
    'bands?',
    'dress to',
    'mixtape',
    'decks',
    'r&b',
    'local dj\W?s?',
    'all night',
    'lounge',
    'live performances?',
    'doors', # doors open at x
    'restaurant',
    'hotel',
    'music shows?',
    'a night of',
    'dance floor',
    'beer',
    'bartenders?',
    'waiters?',
    'waitress(?:es)?',
    'go\W?go',
]

#TODO(lambert): use these
preprocess_removals = [
    # positive
    'tap water', # for theo and dominque's jam

    # negative
    "america's got talent",
    'jerk chicken',
    'poker tournaments?',
    'fashion competition',
    'wrestling competition',
    't?shirt competition',
    'shaking competition',
    'costume competition',
    'bottles? popping?',
    'poppin.? bottles?',
    'dance fitness',
    'lock down',
    'lock up',
    'latin street dance',
    'whack music',
    'wack music',
    'marvellous dance crew',
    '1st class',
    'first class',
    'world class',
    'go\W?go\W?danc(?:ers?|ing?)',
    'latin street',
    'ice\w?breaker',
]

# battle freestyle ?
# dj battle
# battle royale
# http://www.dancedeets.com/events/admin_edit?event_id=208662995897296
# mc performances
# beatbox performances
# beat 
# 'open cyphers'
# freestyle
#in\Whouse  ??
# 'brad houser'

# open mic

#dj.*bboy
#dj.*bgirl

# 'vote for xx' in the subject
# 'vote on' 'vote for' in body, but small body of text
# release party

# methodology
# cardio
# fitness

# sometimes dance performances have Credits with a bunch of other performers, texts, production, etc. maybe remove these?

# HIP HOP INTERNATIONAL

# bad words in title of club events
# DJ
# Live
# Mon/Tue/Wed/Thu/Fri/Sat
# Guests?
# 21+ 18+

# boogiezone if not contemporary?
# free style if not salsa?


#TODO(lambert): use these to filter out shows we don't really care about
other_show_keywords = [
    'comedy',
    'poetry',
    'poets?',
    'spoken word',
    'painting',
    'juggling',
    'magic',
    'singing',
    'acting',
]

cypher_keywords = [
    'c(?:y|i)ph(?:a|ers?)',
    u'サイファ', # japanese cypher
    u'サイファー', # japanese cypher
    u'サークル', # japanese circle
    u'サーク', # japanese circle
    'cerchi', # italian circle/cypher
    u'ไซเฟอร์', # thai cypher
    u'싸이퍼.?', # korean cypher
]

battle_keywords = [
    'apache line',
    'battle of the year', 'boty', 'compete',
    'competitions?',
    'konkurrence', # danish competition
    'competencia', # spanish competition
    u'competición', # spanish competition
    u'compétition', # french competition
    u'thi nhảy', # dance competition vietnam
    'kilpailu\w*' # finish competition
    'konkursams', # lithuanian competition
    'verseny', # hungarian competition
    'championships?',
    'champs?',
    u'čempionatams', # lithuanian championship
    'campeonato', # spanish championship
    'meisterschaft', # german championship
    'concorsi', # italian competition
    u'danstävling', # swedish dance competition
    u'แข่งขัน', # thai competition
    'crew battle[sz]?', 'exhibition battle[sz]?',
    'battles?',
    'battlu(?:je)?', # french czech
    u'比賽', # chinese battle
    u'バトル', # japanese battle
    u'битката', # bulgarian battle
    'batallas', # battles spanish
    'zawody', # polish battle/contest
    'walki', # polish battle/fight
    u'walkę', # polish battle/fight
    'bitwa', # polish battle
    u'bitwę', # polish battle
    'bitwach', # polish battle
    u'バトル', # japanese battle
    'tournaments?',
    'tournoi', # french tournament
    u'大会', # japanese tournament
    u'トーナメント', # japanese tournament
    'turnie\w*', # tournament polish/german
    u'giải đấu', # tournament vietnamese
    u'thi đấu', # competition vietnamese
    u'състезанието', # competition bulgarian
    u'đấu', # game vietnamese
    'turneringer', # danish tournament
    'preselections?',
    u'présélections?', # preselections french
    r'(?:seven|7)\W*(?:to|two|2)\W*(?:smoke|smook|somke)',
    'crew\W?v[sz]?\W?crew',
    'bonnie\s*(?:and|&)\s*clyde',
    'prelims?',
    u'初賽', # chinese preliminaries
]


class_keywords = [
    'work\W?shop\W?s?',
    'ws', # japanese workshop WS
    'w\.s\.', # japanese workshop W.S.
    u'ワークショップ', # japanese workshop
    'cursillo', # spanish workshop
    'ateliers', # french workshop
    'workshopy', # czech workshop
    u'סדנאות', # hebrew workshops
    u'סדנה', # hebew workshop
    # 'taller', # workshop spanish
    'delavnice', # workshop slovak
    'talleres', # workshops spanish
    'radionicama', # workshop croatian
    'warsztaty', # polish workshop
    u'warsztatów', # polish workshop
    u'seminarų', # lithuanian workshop
    'taller de', # spanish workshop
    'intensives?',
    'intensivo', # spanish intensive
    'class with', 'master\W?class(?:es)?',
    'company class',
    u'мастер-класса?', # russian master class
    u'классa?', # russian class
    'class(?:es)?', 'lessons?', 'courses?',
    'klass(?:en)?', # slovakian class
    u'수업', # korean class
    u'수업을', # korean classes
    'lekc[ie]', # czech lesson
    u'課程', # course chinese
    u'課', # class chinese
    u'堂課', # lesson chinese
    u'コース', # course japanese
    'concorso', # course italian
    'kurs(?:y|en)?', # course german/polish
    'aulas?', # portuguese class(?:es)?
    u'특강', # korean lecture
    'lektion(?:en)?', # german lecture
    'lekcie', # slovak lessons
    'dansklasser', # swedish dance classes
    'lekcj[ai]', # polish lesson
    'eigoje', # lithuanian course
    'pamokas', # lithuanian lesson
    'kursai', # course lithuanian
    'lez.', #  lesson italian
    'lezione', # lesson italian
    'lezioni', # lessons italian
    u'zajęciach', # class polish
    u'zajęcia', # classes polish
    u'คลาส', # class thai
    'classe', # class italian
    'classi', # classes italin
    'klasser?', # norwegian class
    'cours', 'clases?',
    'camp',
    'kamp',
    'kemp',
    'formazione', # training italian
    'formazioni', # training italian
    u'トレーニング', # japanese training
]

audition_keywords = [
    'try\W?outs?',
    'casting',
     'casting call',
    'castingul', # romanian casting
    'auditions?',
    'audicija', # audition croatia
    'audiciones', # spanish audition
    'konkurz', # audition czech
    u'試鏡', # chinese audition
    'audizione', # italian audition
    'naborem', # polish recruitment/audition
]

event_keywords = [
    'open circles',
    'session', # the plural 'sessions' is handled up above under club-and-event keywords
    u'セッション', # japanese session
    u'練習会', # japanese training
    u'練習', # japanese practice
    'abdc', 'america\W?s best dance crew',
]

english_digit_x_keywords = [
    'v/s',
    r'vs?\.?',
    'on',
    'x',
    u'×',
]
digit_x_keywords = english_digit_x_keywords + [
    'na',
    'mot',
    'contra',
    'contre',
]
digit_x_string = '|'.join(digit_x_keywords)
english_digit_x_string = '|'.join(english_digit_x_keywords)
n_x_n_keywords = [u'%s[ -]?(?:%s)[ -]?%s' % (i, digit_x_string, i) for i in range(12)[1:]]
n_x_n_keywords += [u'%s[ -](?:%s)[ -]%s' % (i, english_digit_x_string, i) for i in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']]
event_keywords += class_keywords
event_keywords += n_x_n_keywords
event_keywords += battle_keywords
event_keywords += audition_keywords
event_keywords += cypher_keywords

judge_keywords = [
    'jurys?',
    'jurados?', # spanish jury
    u'журито', # bulgarian jury
    'judge[sz]?',
    'jures', # french jury
    '(?:les? )?juges?', # french judges
    'giudici', # italian judges
    u'השופט', # hebrew judge
    u'השופטים', # hebrew judges
    u'teisėjai', # lithuanian judges
    'tuomaristo', # jury finnish
    'jueces', # spanish judges
    'juriu', # romanian judges
    'giuria', # jury italian
    u'評審', # chinese judges
    u'評判', # chinese judges
    u'評判團', # chinese judges
    u'審査員', # japanese judges
    u'ジャッジ', # japanese judges
]
event_keywords += judge_keywords


french_event_keywords = [
    'spectacle',
    'stage',
]

italian_event_keywords = [
    'stage',
]

dance_wrong_style_keywords = [
    'styling', 'salsa', 'bachata', 'balboa', 'tango', 'latin', 'lindy', 'lindyhop', 'swing', 'wcs', 'samba',
    'latines', 'quickstep', 'rumba', 'cha\W?cha',
    'blues',
    'waltz',
    'salsy', # salsa czech
    'salser[oa]s?',
    'kizomba',
    'disco dance',
    'disco tan\w+', # czech disco dance
    'milonga',
    'dance partner',
    'cha cha',
    'hula',
    'tumbling',
    'exotic',
    'cheer',
    'barre',
    'butoh',
    'contato improv\w*',
    'contact improv\w*',
    'contratto mimo', # italian contact mime
    'musical theat(?:re|er)',
    'pole danc\w+', 'flirt danc\w+',
    'go\W?go',
    'bollywood', 'kalbeliya', 'bhawai', 'teratali', 'ghumar',
    'indienne',
    'persiana?',
    'arabe', 'arabic', 'araba',
    'oriental\w*', 'oriente', 
    'cubana',
    'capoeira',
    'tahitian dancing',
    'tahitienne',
    'folklor\w+',
    'kizomba',
    'burlesque',
    u'バーレスク', # burlesque japan
    'limon',
    'artist\Win\Wresidence',
    'residency',
    'disciplinary',
    'reflective',
    'clogging',
    'zouk',
    'african dance',
    'afro dance',
    'afro mundo',
    'class?ic[ao]',
    'acroyoga',
    'kirtan',
    'hoop\W?dance',
    'modern dance',
    'pilates',
    'tribal',
    'jazz', 'tap', 'contemporary',
    u'súčasný', # contemporary slovak
    u'współczesnego', # contemporary polish
    'contempor\w*', # contemporary italian, french
    'africa\w+',
    'sabar',
    'aerial silk',
    'silk',
    'aerial',
    'zumba', 'belly\W?danc(?:e(?:rs?)?|ing)', 'bellycraft', 'worldbellydancealliance',
    'soca',
    'flamenco',
    'technique',
    'guest artists?',
    'partnering',
    'charleston',
]
dance_wrong_style_title_keywords = dance_wrong_style_keywords + [
    # Sometimes used in studio name even though it's still a hiphop class:
    'ballroom',
    'ballet',
    'yoga',
    'talent shows?', # we don't care about talent shows that offer dance options
    'stiletto',
    '\w+ball', # basketball/baseball/football tryouts
]

all_regexes = {}

grouped_manual_dance_keywords = {}

INDEPENDENT_KEYWORD = 0
DEPENDENT_KEYWORD = 1

#TODO(lambert): maybe handle 'byronom coxom' in slovakian with these keywords
def get_manual_dance_keywords(filename):
    manual_keywords = []
    dependent_manual_keywords = []
    import os
    if os.getcwd().endswith('mapreduce'): #TODO(lambert): what is going on with appengine sticking me in the wrong starting directory??
        base_dir = '..'
    else:
        base_dir = '.'

    f = codecs.open('%s/dance_keywords/%s.txt' % (base_dir, filename), encoding='utf-8')
    for line in f.readlines():
        line = re.sub('\s*#.*', '', line.strip())
        if not line:
            continue
        if line.endswith(',0'):
            line = line[:-2]
            dependent_manual_keywords.append(line)
        else:
            manual_keywords.append(line)

    result = [None, None]
    result[INDEPENDENT_KEYWORD] = manual_keywords
    result[DEPENDENT_KEYWORD] = dependent_manual_keywords
    return result

manual_keywords = {}
manual_dance_keywords = []
dependent_manual_dance_keywords = []
manual_dancers = []
dependent_manual_dancers = []

def build_regexes():
    global manual_keywords
    global manual_dance_keywords, dependent_manual_dance_keywords
    global manual_dancers, dependent_manual_dancers
    if 'good_capturing_keyword_regex' in all_regexes:
        return

    dancer_keyword_files = ['bboy_crews', 'bboys', 'choreo_crews', 'choreo_dancers', 'freestyle_crews', 'freestyle_dancers']
    extra_keyword_files = ['choreo_keywords', 'freestyle_keywords', 'competitions', 'good_djs']

    for filename in dancer_keyword_files + extra_keyword_files:
        manual_keywords[filename] = get_manual_dance_keywords(filename)
    manual_dancers = []
    dependent_manual_dancers = []
    for filename in dancer_keyword_files:
        manual_dancers += manual_keywords[filename][INDEPENDENT_KEYWORD]
        dependent_manual_dancers += manual_keywords[filename][DEPENDENT_KEYWORD]
    manual_keywords['manual_dancers'] = [None, None]
    manual_keywords['manual_dancers'][INDEPENDENT_KEYWORD] = manual_dancers
    manual_keywords['manual_dancers'][DEPENDENT_KEYWORD] = dependent_manual_dancers

    manual_dance_keywords = manual_dancers[:]
    dependent_manual_dance_keywords = dependent_manual_dancers[:]
    for filename in extra_keyword_files:
        manual_dance_keywords += manual_keywords[filename][INDEPENDENT_KEYWORD]
        dependent_manual_dance_keywords += manual_keywords[filename][DEPENDENT_KEYWORD]
    manual_keywords['manual_dance_keywords'] = [None, None]
    manual_keywords['manual_dance_keywords'][INDEPENDENT_KEYWORD] = manual_dance_keywords
    manual_keywords['manual_dance_keywords'][DEPENDENT_KEYWORD] = dependent_manual_dance_keywords

    for keyword, x in manual_keywords.iteritems():
        if x[INDEPENDENT_KEYWORD]:
            all_regexes['%s_regex' % keyword] = make_regexes(x[INDEPENDENT_KEYWORD])
        else:
            all_regexes['%s_regex' % keyword] = make_regexes(r'NEVER_MATCH_BLAGSDFSDFSEF')
        if x[INDEPENDENT_KEYWORD] + x[DEPENDENT_KEYWORD]:
            all_regexes['extended_%s_regex' % keyword] = make_regexes(x[INDEPENDENT_KEYWORD] + x[DEPENDENT_KEYWORD])
        else:
            all_regexes['%s_regex' % keyword] = make_regexes(r'NEVER_MATCH_BLAGSDFSDFSEF')

    all_regexes['good_keyword_regex'] = make_regexes(easy_dance_keywords + easy_event_keywords + dance_keywords + event_keywords + club_and_event_keywords + dance_and_music_keywords + easy_choreography_keywords + manual_dance_keywords + dependent_manual_dance_keywords, wrapper='(?i)%s')
    all_regexes['good_capturing_keyword_regex'] = make_regexes(easy_dance_keywords + easy_event_keywords + dance_keywords + event_keywords + club_and_event_keywords + dance_and_music_keywords + easy_choreography_keywords + manual_dance_keywords + dependent_manual_dance_keywords, matching=True, wrapper='(?i)%s')

def make_regex(strings, match_cjk, matching=False, wrapper='%s', flags=0):
    try:
        regex = make_regex_string(strings, matching=matching, word_boundaries=True, match_cjk=match_cjk, wrapper=wrapper)
        if re2:
            return re.compile(regex, max_mem=15000000, flags=flags)
        else:
            return re.compile(regex, flags=flags)
    except UnicodeDecodeError:
        for line in strings:
            try:
                re.compile(u'|'.join([line]), re.UNICODE)
            except UnicodeDecodeError:
                logging.error("failed to compile: %r: %s", line, line)
                raise
        logging.fatal("Error constructing regexes")

NO_WORD_BOUNDARIES = 0
WORD_BOUNDARIES = 1
def make_regexes(strings, matching=False, wrapper='%s', flags=0):
    a = [None] * 2
    a[NO_WORD_BOUNDARIES] = make_regex(strings, matching=matching, match_cjk=True, wrapper=wrapper, flags=flags)
    a[WORD_BOUNDARIES] = make_regex(strings, matching=matching, match_cjk=False, wrapper=wrapper, flags=flags)
    return tuple(a)

all_regexes['preprocess_removals_regex'] = make_regexes(preprocess_removals)
all_regexes['dance_wrong_style_regex'] = make_regexes(dance_wrong_style_keywords)
all_regexes['judge_keywords_regex'] = make_regexes(judge_keywords)
all_regexes['audition_regex'] = make_regexes(audition_keywords)
all_regexes['battle_regex'] = make_regexes(battle_keywords)
all_regexes['n_x_n_regex'] = make_regexes(n_x_n_keywords)
all_regexes['dance_wrong_style_title_regex'] = make_regexes(dance_wrong_style_title_keywords)
all_regexes['dance_and_music_regex'] = make_regexes(dance_and_music_keywords)
all_regexes['class_regex'] = make_regexes(class_keywords)
all_regexes['club_and_event_regex'] = make_regexes(club_and_event_keywords)
all_regexes['easy_choreography_regex'] = make_regexes(easy_choreography_keywords)
all_regexes['club_only_regex'] = make_regexes(club_only_keywords)

all_regexes['easy_dance_regex'] = make_regexes(easy_dance_keywords)
all_regexes['easy_event_regex'] = make_regexes(easy_event_keywords)
all_regexes['dance_regex'] = make_regexes(dance_keywords)
all_regexes['event_regex'] = make_regexes(event_keywords)
all_regexes['french_event_regex'] = make_regexes(event_keywords + french_event_keywords)
all_regexes['italian_event_regex'] = make_regexes(event_keywords + italian_event_keywords)

all_regexes['bad_capturing_keyword_regex'] = make_regexes(club_only_keywords + dance_wrong_style_keywords, matching=True)

all_regexes['italian'] = make_regexes(['di', 'i', 'e', 'con'])
all_regexes['french'] = make_regexes(["l'\w*", 'le', 'et', 'une', 'avec', u'à', 'pour'])

# NOTE: Eventually we can extend this with more intelligent heuristics, trained models, etc, based on multiple keyword weights, names of teachers and crews and whatnot

def get_relevant_text(fb_event):
    # use a separator here, so 'actors workshop' 'breaking boundaries...' doesn't match 'workshop breaking'
    search_text = (fb_event['info'].get('name', '') + ' . . . . ' + fb_event['info'].get('description', '')).lower()
    return search_text

class ClassifiedEvent(object):
    def __init__(self, fb_event, language=None):
        self.fb_event = fb_event
        if 'name' not in fb_event['info']:
            logging.info("fb event id is %s has no name, with value %s", fb_event['info']['id'], fb_event)
            self.search_text = ''
            self.title = ''
        else:
            self.search_text = get_relevant_text(fb_event)
            self.title = fb_event['info'].get('name', '').lower()
        self.language = language
        self.times = {}

    def classify(self):
        build_regexes()

        #self.language not in ['ja', 'ko', 'zh-CN', 'zh-TW', 'th']:
        if cjk_detect.cjk_regex.search(self.search_text):
            cjk_chars = len(cjk_detect.cjk_regex.findall(self.search_text))
            if 1.0 * cjk_chars / len(self.search_text) > 0.05:
                self.boundaries = NO_WORD_BOUNDARIES
            else:
                self.boundaries = WORD_BOUNDARIES
        else:
            self.boundaries = WORD_BOUNDARIES
        idx = self.boundaries

        self.final_search_text = all_regexes['preprocess_removals_regex'][idx].sub('', self.search_text)
        search_text = self.final_search_text
        self.final_title = all_regexes['preprocess_removals_regex'][idx].sub('', self.title)
        title = self.final_title

        #if not all_regexes['good_keyword_regex'][idx].search(search_text):
        #    self.dance_event = False
        #    return
        a = time.time()
        b = time.time()
        self.manual_dance_keywords_matches = all_regexes['manual_dance_keywords_regex'][idx].findall(search_text)
        self.times['manual_regex'] = time.time() - b
        easy_dance_matches = all_regexes['easy_dance_regex'][idx].findall(search_text)
        easy_event_matches = all_regexes['easy_event_regex'][idx].findall(search_text)
        self.real_dance_matches = all_regexes['dance_regex'][idx].findall(search_text)
        if all_regexes['french'][idx].search(search_text):
            event_matches = all_regexes['french_event_regex'][idx].findall(search_text)
        elif all_regexes['italian'][idx].search(search_text):
            event_matches = all_regexes['italian_event_regex'][idx].findall(search_text)
        else:
            event_matches = all_regexes['event_regex'][idx].findall(search_text)
        dance_wrong_style_matches = all_regexes['dance_wrong_style_regex'][idx].findall(search_text)
        dance_and_music_matches = all_regexes['dance_and_music_regex'][idx].findall(search_text)
        club_and_event_matches = all_regexes['club_and_event_regex'][idx].findall(search_text)
        easy_choreography_matches = all_regexes['easy_choreography_regex'][idx].findall(search_text)
        club_only_matches = all_regexes['club_only_regex'][idx].findall(search_text)
        self.times['all_regexes'] = time.time() - a

        self.found_dance_matches = self.real_dance_matches + easy_dance_matches + dance_and_music_matches + self.manual_dance_keywords_matches + easy_choreography_matches
        self.found_event_matches = event_matches + easy_event_matches + club_and_event_matches
        self.found_wrong_matches = dance_wrong_style_matches + club_only_matches

        title_wrong_style_matches = all_regexes['dance_wrong_style_regex'][idx].findall(title)
        title_good_matches = all_regexes['good_keyword_regex'][idx].findall(title)
            
        combined_matches = self.found_dance_matches + self.found_event_matches
        words = re.split(r'\W+', re.sub(r'\bhttp.*?\s', '', search_text))
        fraction_matched = 1.0 * len(combined_matches) / len(words)
        if not fraction_matched:
            self.calc_inverse_keyword_density = 100
        else:
            self.calc_inverse_keyword_density = -int(math.log(fraction_matched, 2))

        #strong = 0
        #for line in search_text.split('\n'):
        #    matches = all_regexes['good_keyword_regex'][idx].findall(line)
        #    good_parts = sum(len(x) for x in matches)
        #    if 1.0 * good_parts / len(line) > 0.1:
        #        # strong!
        #        strong += 1
        
        if len(self.manual_dance_keywords_matches) >= 1:
            self.dance_event = 'obvious dancer or dance crew or battle'
        # one critical dance keyword
        elif len(self.real_dance_matches) >= 1:
            self.dance_event = 'obvious dance style'
        # If the title has a bad-style and no good-styles, mark it bad
        elif (all_regexes['dance_wrong_style_title_regex'][idx].search(title) and
            not (
                all_regexes['dance_and_music_regex'][idx].search(title) or
                self.manual_dance_keywords_matches or
                self.real_dance_matches)): # these two are implied by the above, but do it here just in case future clause re-ordering occurs
            self.dance_event = False

        elif len(dance_and_music_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1 and self.calc_inverse_keyword_density < 5 and not (title_wrong_style_matches and not title_good_matches):
            self.dance_event = 'hiphop/funk and good event type'
        # one critical event and a basic dance keyword and not a wrong-dance-style and not a generic-club
        elif len(easy_dance_matches) >= 1 and (len(event_matches) + len(easy_choreography_matches)) >= 1 and len(dance_wrong_style_matches) == 0 and self.calc_inverse_keyword_density < 5:
            self.dance_event = 'dance event thats not a bad-style'
        elif len(easy_dance_matches) >= 1 and len(club_and_event_matches) >= 1 and len(dance_wrong_style_matches) == 0 and len(club_only_matches) == 0:
            self.dance_event = 'dance show thats not a club'
        else:
            self.dance_event = False
        self.times['all_match'] = time.time() - a

    def is_dance_event(self):
        return bool(self.dance_event)
    def reason(self):
        return self.dance_event
    def dance_matches(self):
        return set(self.found_dance_matches)
    def event_matches(self):
        return set(self.found_event_matches)
    def wrong_matches(self):
        return set(self.found_wrong_matches)
    def match_score(self):
        if self.is_dance_event():
            combined_matches = self.found_dance_matches + self.found_event_matches
            return len(combined_matches)
        else:
            return 0
    def inverse_keyword_density(self):
        return self.calc_inverse_keyword_density


def get_classified_event(fb_event, language=None):
    classified_event = ClassifiedEvent(fb_event, language)
    classified_event.classify()
    return classified_event

def relevant_keywords(fb_event):
    build_regexes()
    text = get_relevant_text(fb_event)
    if cjk_detect.cjk_regex.search(text):
        idx = NO_WORD_BOUNDARIES
    else:
        idx = WORD_BOUNDARIES
    good_keywords = all_regexes['good_capturing_keyword_regex'][idx].findall(text)
    bad_keywords = all_regexes['bad_capturing_keyword_regex'][idx].findall(text)
    return sorted(set(good_keywords).union(bad_keywords))

@skip_filter
def highlight_keywords(text):
    build_regexes()
    if cjk_detect.cjk_regex.search(text):
        idx = NO_WORD_BOUNDARIES
    else:
        idx = WORD_BOUNDARIES
    text = all_regexes['good_capturing_keyword_regex'][idx].sub('<span class="matched-text">\\1</span>', text)
    text = all_regexes['bad_capturing_keyword_regex'][idx].sub('<span class="bad-matched-text">\\1</span>', text)
    return text

if __name__ == '__main__':
    a = ['club', 'bottle service', 'table service', 'coat check', 'free before', 'vip', 'guest\\W?list', 'drink specials?', 'resident dj\\W?s?', 'dj\\W?s?', 'techno', 'trance', 'indie', 'glitch', 'bands?', 'dress to', 'mixtape', 'decks', 'r&b', 'local dj\\W?s?', 'all night', 'lounge', 'live performances?', 'doors', 'restaurant', 'hotel', 'music shows?', 'a night of', 'dance floor', 'beer', 'blues', 'bartenders?', 'waiters?', 'waitress(?:es)?', 'go\\Wgo', 'gogo', 'styling', 'salsa', 'bachata', 'balboa', 'tango', 'latin', 'lindy', 'lindyhop', 'swing', 'wcs', 'samba', 'waltz', 'salsy', 'milonga', 'dance partner', 'cha cha', 'hula', 'tumbling', 'exotic', 'cheer', 'barre', 'contact improv', 'contact improv\\w*', 'contratto mimo', 'musical theat(?:re|er)', 'pole dance', 'flirt dance', 'bollywood', 'kalbeliya', 'bhawai', 'teratali', 'ghumar', 'indienne', 'persiana?', 'arabe', 'arabic', 'oriental\\w*', 'oriente', 'cubana', 'capoeira', 'tahitian dancing', 'folklor\\w+', 'kizomba', 'burlesque', 'technique', 'limon', 'clogging', 'zouk', 'afro mundo', 'class?ic[ao]', 'acroyoga', 'kirtan', 'modern dance', 'pilates', 'tribal', 'jazz', 'tap', 'contemporary', 'contempor\\w*', 'africa\\w+', 'sabar', 'silk', 'aerial', 'zumba', 'belly\\W?danc(?:e(?:rs?)?|ing)', 'bellycraft', 'worldbellydancealliance', 'soca', 'flamenco']
    a = sorted(a)
    print a
    print re_flatten.construct_regex(a)
    print highlight_keywords(u' ๆ ซึ่งไม่ให้พี่น้อง Bboy ได้ผิดหวังอีกต่อไป*')
    print highlight_keywords('matched-text')
