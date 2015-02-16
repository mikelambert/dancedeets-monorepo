# -*-*- encoding: utf-8 -*-*-
#

import itertools
import re
import regex_keywords
from util import re_flatten

# The magical repository of all dance keywords
_keywords = {}
_regex_strings = {}
_regexes = {}

class GrammarRule(object):
    """The entire grammar rule tree must be composed of these."""

class Keyword(GrammarRule):
    def __init__(self, name, keywords):
        self._name = name
        self._final_name = re.sub(r'[\W_]+', '', self._name)
        self._keywords = tuple(keywords)

    def children(self):
        return []

    def as_expanded_regex(self):
        return get_regex_string(self)

    def as_token_regex(self):
        return r'_%s\d*_' % self._final_name

    def replace_string(self, *args):
        if args:
            extra_hash = abs(hash(args[0]))
        else:
            extra_hash = ''
        return '_%s%s_' % (self._final_name, extra_hash)

    def get_keywords(self):
        return self._keywords

    def __repr__(self):
        return 'Keyword(%r, [...])' % self._name


def _key(tokens):
    return tuple(sorted(tokens))

def get_regex_string(*tokens):
    token_key = _key(tokens)
    if token_key not in _regex_strings:
        _regex_strings[token_key] = re_flatten.construct_regex(get(*tokens) + [token.as_token_regex() for token in tokens])
    return _regex_strings[token_key]

#TODO(lambert): move this function out of here in some way, as it is an artifact of the old-way
def get_regex(*tokens):
    token_key = _key(tokens)
    if token_key not in _regexes:
        # TODO(lambert): this is regexes, while function name is regex. We need to fix this (since make_regex is a different function)
        _regexes[token_key] = regex_keywords.make_regexes(get(*tokens) + [token.as_token_regex() for token in tokens])
    return _regexes[token_key]

def _flatten(listOfLists):
    "Flatten one level of nesting"
    return list(itertools.chain.from_iterable(listOfLists))

def get(*tokens):
    return _flatten(token.get_keywords() for token in tokens)

# Set up in event_classifier.py
MANUAL_DANCER = None
MANUAL_DANCE = None


# 'crew' biases dance one way, 'company' biases it another
EASY_DANCE = Keyword('EASY_DANCE', [
    'dance style[sz]',
    'dances?', "dancin[g']?", 'dancers?',
    u'رقص', # arabic dance
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
    u'舞.?蹈', # chinese dance
    u'舞', # chinese dance
    u'排舞', # chinese dance
    u'蹈', # chinese dance
    u'跳.?舞', # chinese dance
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

EASY_CHOREO = Keyword('EASY_CHOREO', [
    u'(?:ch|k|c)oe?re[o|ó]?gra(?:ph|f)\w*', #english, italian, finnish, swedish, german, lithuanian, polish, italian, spanish, portuguese, danish
    'choreo',
    u'chorée', # french choreo
    u'chorégraph\w*', # french choreographer
    u'кореограф', # macedonian
    u'안무',
])

GOOD_INSTANCE_OF_BAD_CLUB = Keyword('GOOD_INSTANCE_OF_BAD_CLUB', [
    'evelyn\W+champagne\W+king',
    'water\W?bottles?',
    'genie in (?:the|a) bottle',
])

BAD_CLUB = Keyword('BAD_CLUB', [
    'bottle\W?service',
    'popping?\W?bottles?',
    'bottle\W?popping?',
    'bottles?',
    'grey goose',
    'champagne',
    'belvedere',
    'ciroc',
])

CYPHER = Keyword('CYPHER', [
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

AMBIGUOUS_DANCE_MUSIC = Keyword('AMBIGUOUS_DANCE_MUSIC', [
    'hip\W?hop',
    u'嘻哈', # chinese hiphop
    u'ההיפ הופ', # hebrew hiphop
    u'هيب هوب', # arabic hiphop
    u'хипхоп', # macedonian hiphop
    u'ヒップホップ', # hiphop japanese
    u'힙합', # korean hiphop
    'hip\W?hop\w*', # lithuanian, polish hiphop
    'all\W?style[zs]?',
    'tou[ts]\W?style[zs]?', # french all-styles
    'tutti gli stili', # italian all-styles
    'kaikille tyyleille avoin', # finnish all-styles
    'be\W?bop',
    'shuffle',
    'funk',
    'dance\W?hall\w*',
    'ragga',
    u'레게', # korean reggae
    'hype',
    'new\W?jack\W?swing',
    'gliding', 
    # 'breaks', # too many false positives
    'boogaloo',
    "breakin[g']?", 'breakers?',
    'jerk',
    'kpop',
    u'케이팝', # korean kpop
    'rnb',
    "poppin\'?",
    'hard\Whitting',
    'electro\W?dance',
    'old\W?school hip\W?hop',
    '90\W?s hip\W?hop',
    u'フリースタイル', # japanese freestyle
    u'얼반', # korean urban
])

STYLE_BREAK = Keyword('STYLE_BREAK', [
    'breakingu', #breaking polish
    u'breaktánc', # breakdance hungarian
    u'ブレイク', # breakdance japanese
    "bre?ak\W?dancin[g']?", 'bre?ak\W?dancer?s?',
    'break\W?danc\w+',
    'power\W?moves?',
    'b\W?(?:boy|girl)\w*',
    u'비보이', # korean bboy
    u'비걸', # korean bgirl
    u'파워무브', # powermove korean
    'breakeuse', # french bgirl
    u'탑락', # toprock
])
# Crazy polish sometimes does lockingu and lockingy. Maybe we need to do this more generally though.
#add(STYLE_BREAK, [x+'u' for x in legit_dance])
STYLE_ROCK = Keyword('STYLE_ROCK', [
    'rock\W?dan[cs]\w+',
    "top\W?rock(?:s|er[sz]?|in[g']?)?", "up\W?rock(?:s|er[sz]?|in[g']?|)?",
])
STYLE_POP = Keyword('STYLE_POP', [
    'funk\W?style[sz]?',
    'poppers?', 'popp?i?ng', # listing poppin in the ambiguous keywords
    'poppeurs?',
    u'팝핀', # korean popping
    "pop\W{0,3}(?:(?:N|and|an)\W{1,3})?lock(?:in[g']?|er[sz]?)", # dupe
    "wavin[g']?", 'wavers?',
    'liquid\W+dance'
    'liquid\W+(?:\w+\W+)?digitz',
    u'리퀴드댄싱', # korean liquid dance
    'finger\W+digitz',
    'toy\W?man',
    'puppet\W?style',
    "bott?in[g']?",
    "robott?in[g']?",
    u'로봇팅', # roboting
    'g\W?styl\w+',
    'strutter[sz]?', 'strutting',
    u'스트럿팅', # strutting
    "tuttin[g']?", 'tutter[sz]?',
    u'텃팅', # korean tutting
])
STYLE_LOCK = Keyword('STYLE_LOCK', [
    "pop\W{0,3}(?:(?:N|and|an)\W{1,3})?lock(?:in[g']?|er[sz]?)", # dupe
    "lock(?:er[sz]?|in[g']?)?", 'lock dance',
    u'ロッカーズ', # japanese lockers
    u'ロッカ', # japanese lock
    u'락킹', # korean locking
    'locking4life',
])
STYLE_WAACK = Keyword('STYLE_WAACK', [
    "[uw]h?aa?c?c?k(?:er[sz]?|inn?[g']?)", # waacking
    u'왁킹', # korean waacking
    u'ワッキング', # japanese waacking
    u'パーンキング', # japanese punking
    "paa?nc?kin[g']?", # punking
])
STYLE_ALLSTYLE = Keyword('STYLE_ALLSTYLE', [
    'mix(?:ed)?\W?style[sz]?', 'open\W?style[sz]',
    'all\W+open\W?style[sz]?',
    'open\W+all\W?style[sz]?',
    'me against the music',
])

legit_dance = [
    'street\W?jam',
    'jazz rock',
    u'재즈 ?록', # korean jazz rock
    'commercial hip\W?hop',
    'lyrical\Whip\W?',
    'hip\W?hop dance',
    "jerk(?:ers?|in[g']?)",
    u'스트릿', # street korean
    u'ストリートダンス', # japanese streetdance
    u'رقص الشوارع', # arabic streetdance
    u'البريك دانس', # arabic breakdance
    u'街舞', # chinese streetdance / hiphop
    u'gatvės šokių', # lithuanian streetdance
    'katutanssi\w*', # finnish streetdance
    '(?:lite|light)\W?feet',
    "gettin[g']?\W?(?:lite|light)",
    "turfin(?:[g']?|er[sz])", 'turf danc\w+', "flexin[g']?", "buckin[g']?", "jookin[g']?",
    "footworkin[g']?",
    'footworks', # spanish footworks
    u'フットワーキング', # japanese footworking
    'houser[sz]?',
    'afro\W?house',
    'dance house', # seen in italian
    'soul dance',
    u'ソウルダンス', # soul dance japanese
    #'soul train',...do we want this?
    u'소울트레인', # korean soul train
    'dance crew[sz]?',
    u'댄스 ?승무원', # korean dance crew
    'melbourne shuffle',
    'mj\W+style', 'michael jackson style',
    'mtv\W?style', 'mtv\W?dance', 'videoclip\w+', 'videodance',
    'hip\W?hop\Wheels',
    # only do la-style if not salsa? http://www.dancedeets.com/events/admin_edit?event_id=292605290807447
    # 'l\W?a\W?\Wstyle',
    'l\W?a\W?\Wdance',
    'n(?:ew|u)\W?style\Whip\W?hop',
    u'뉴스타일 ?힙합', # korean new style hiphop
    'hip\W?hop\Wn(?:ew|u)\W?style',
    'krump', "krumpin[g']?", 'krumper[sz]?',
    u'크럼핑', # korean krumping
    'ragga\W?jamm?',
    u'댄스 ?레게', # korean reggae dance
    u'레게 ?댄스', # korean reggae dance
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
    'new\W?style hustle',
    'urban danc\w*',
    'urban style[sz]',
    'urban contemporary',
    u'dan[çc]\w* urban\w*',
    'dan\w+ urbai?n\w+', # spanish/french urban dance
    'baile urbai?n\w+', # spanish urban dance
    'estilo\w* urbai?n\w+', # spanish urban styles
]

# hiphop dance. hiphop dans?
# Crazy polish sometimes does lockingu and lockingy. Maybe we need to do this more generally though.
DANCE = Keyword('DANCE', legit_dance + [x+'u' for x in legit_dance])
# TODO(lambert): Is this a safe one to add?
# http://en.wikipedia.org/wiki/Slovak_declension
# dance_keywords = dance_keywords + [x+'y' for x in dance_keywords] 

# hiphop dance. hiphop dans?

# house battles http://www.dancedeets.com/events/admin_edit?event_id=240788332653377
HOUSE = Keyword('HOUSE', [
    'house',
    u'하우스', # korean house
    u'ハウス', # japanese house
    u'хаус', # russian house
])

FREESTYLE = Keyword('FREESTYLE', [
    'free\W?style(?:r?|rs?)',
])

STREET = Keyword('STREET', [
    'street',
    u'스트리트', # korean street
])

EASY_BATTLE = Keyword('EASY_BATTLE', [
    'jams?', 
    'jamit', # finnish jams
    u'잼', # korean jam
])

EASY_EVENT = Keyword('EASY_EVENT', [
    'club', 'after\Wparty', 'pre\Wparty',
    u'클럽', # korean club
    u'クラブ',  # japanese club
    'open sessions?',
    u'오픈 ?세션', # open session
    'training',
])

CONTEST = Keyword('CONTEST', [
    'contests?',
    'concours', # french contest
    'konkurrencer', # danish contest
    'dancecontests', # dance contests german
])
PRACTICE = Keyword('PRACTICE', [
    'sesja', # polish session
    'sessions', 'practice',
    u'연습', # korean practice/runthrough
])

PERFORMANCE = Keyword('PERFORMANCE', [
    'shows?', 'performances?',
    'show\W?case',
    u'représentation', # french performance
    u'퍼포먼스', # korean performance
    u'쇼케이스', # korean showcase
    u'ショーケース', # japanese showcase
    u'成果發表會', # chinese 'result presentation' (final performance)
    u'秀', # chinese show
    u'公演', # chinese performance
    u'展', # chinese exhibition/show
    u'果展', # chinese exhibition
    u'表演', # chinese performance
    u'vystoupení', # czech performances
    u'výkonnostních', # czech performance
    u'изпълнението', # bulgarian performance
    u'パフォーマンス', # japanese performance
    # maybe include 'spectacle' as well?
    'esibizioni', #italian performance/exhibition
])


CLUB_ONLY = Keyword('CLUB_ONLY', [
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
])

PREPROCESS_REMOVAL = Keyword('PREPROCESS_REMOVAL', [
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
    'pledge class',
    'world\Wclass',
    'top class',
    'class\W?rnb',
    'class act',
    'go\W?go\W?danc(?:ers?|ing?)',
    'latin street',
    'ice\W?breaker',

    'straight up', # up rock
    'tear\W?jerker', # jerker
    'in-strutter', # strutter
    'on stage',
    'main\Wstage',
    'of course',
    'breaking down',
    'ground\W?breaking',
    '(?:second|2nd) stage',
    'open house',
    'hip\W?hop\W?kempu?', # refers to hiphop music!
    'camp\W?house',
    'in\W?house',
    'lock in',
    'juste debout school',
    'baile funk',
])

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
#TODO: UNUSED
OTHER_SHOW = Keyword('OTHER_SHOW', [
    'comedy',
    'poetry',
    'poets?',
    'spoken word',
    'painting',
    'juggling',
    'magic',
    'singing',
    'acting',
])



BATTLE = Keyword('BATTLE', [
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
    u'대회에서', # korean competition
    u'선수권대회', # korean champsionship
    u'대회', # korean rally/tournament/etc commonality
    u'대전', # korean battle
    u'배틀', # korean battle
    'crew battle[sz]?', 'exhibition battle[sz]?',
    'battles?',
    'battlu(?:je)?', # french czech
    u'大賽', # chinese competition
    u'比賽', # chinese battle
    u'賽', # chinese race/competition/etc
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
    'prelims?',
    u'初賽', # chinese preliminaries
])

CLASS = Keyword('CLASS', [
    'work\W?shop(?:\W?s)?',
    'ws', # japanese workshop WS
    'w\.s\.', # japanese workshop W.S.
    u'ワークショップ', # japanese workshop
    u'작업장', # korean workshop
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
    'workshoppien', # finnish workshops
    'intensives?',
    'intensivo', # spanish intensive
    'class with', 'master\W?class(?:es)?',
    'company class',
    u'мастер-класса?', # russian master class
    u'классa?', # russian class
    'class(?:es)?', 'lessons?', 'courses?',
    #TODO: should i do a "class(?!ic)"
    'klass(?:en)?', # slovakian class
    u'수업', # korean class
    u'수업을', # korean classes
    'lekc[ie]', # czech lesson
    u'課程', # course chinese
    u'課', # class chinese
    u'堂課', # lesson chinese
    u'表演班', # performance class
    u'專攻班', # chinese specialized class
    u'コース', # course japanese
    'concorso', # course italian
    'kur[sz](?:y|en)?', # course german/polish/czech
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
    u'캠프', # korean camp
    u'營', # chinese camp
    'formazione', # training italian
    'formazioni', # training italian
    u'トレーニング', # japanese training
])

AUDITION = Keyword('AUDITION', [
    'try\W?outs?',
    'casting',
     'casting call',
    'castingul', # romanian casting
    'auditions?',
    'audicija', # audition croatia
    'audiciones', # spanish audition
    'konkurz', # audition czech
    u'オーディション', # japanese audition
    u'トライアウト', # japanese tryout
    u'試鏡', # chinese audition
    u'오디션', # korean audition
    'audizione', # italian audition
    'naborem', # polish recruitment/audition
    'rehearsal',
    u'綵排', # chinese rehearsal
])

EVENT = Keyword('EVENT', [
    'open circles',
    'session', # the plural 'sessions' is handled up above under club-and-event keywords
    u'セッション', # japanese session
    u'練習会', # japanese training
    u'練習', # japanese practice
    'abdc', 'america\W?s best dance crew',
])

def _generate_n_x_n_keywords():
    english_digit_x_keywords = [
        'v/s',
        r'v[zs]?\.?',
        'on',
        'x',
        u'×',
        u':',
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
    n_x_n_keywords += [u'%s[ -](?:%s)[ -]%s' % (i, english_digit_x_string, i) for i in ['crew', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']]
    return n_x_n_keywords

N_X_N = Keyword('N_X_N', _generate_n_x_n_keywords())

JUDGE = Keyword('JUDGE', [
    'jurys?',
    'jurados?', # spanish jury
    u'журито', # bulgarian jury
    'judge[sz]?',
    'jures', # french jury
    '(?:les? )?juges?', # french judges
    'tuomar(?:it)?', # finnish judge(s)
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
    u'심사', # korean judges
])

AMBIGUOUS_CLASS = Keyword('AMBIGUOUS_CLASS', [
    'spectacle',
    'stage',
    'stages',
])

DANCE_WRONG_STYLE = Keyword('DANCE_WRONG_STYLE', [
    'styling', 'salsa', 'bachata', 'balboa', 'tango', 'latin', 'lindy', 'lindyhop', 'swing', 'wcs', 'samba',
    u'サルサ', # japanese salsa
    u'タンゴ', # japanese tango
    u'リンディ', # japanese lindy
    u'소스', # korean salsa
    u'탱고', # korean tango
    u'린디', # korean lindy
    'latines', 'quickstep', 'rumba', 'cha\W?cha',
    u'륨바', # korean rumba
    'blues',
    u'ブルース', # japanese blues
    'waltz',
    u'왈츠', # korean waltz
    u'ワルツ', # japanese waltz
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
    u'舞踏', # japanese butoh
    'contato improv\w*',
    'contact improv\w*',
    u'コンタクトインプロビゼーション', # japanese contact improv
    'contratto mimo', # italian contact mime
    'musical theat(?:re|er)',
    'pole danc\w+', 'flirt danc\w+',
    u'ポールダンス', # japanese pole dance
    u'폴 ?댄스', # korean pole dance
    'go\W?go',
    'bollywood', 'kalbeliya', 'bhawai', 'teratali', 'ghumar',
    u'볼리우드', # bollywood
    'indienne',
    'persiana?',
    'arabe', 'arabic', 'araba',
    'oriental\w*', 'oriente', 
    'cubana',
    'capoeira',
    u'カポエイラ', # japanese capoeira
    'tahitian dancing',
    'tahitienne',
    'folklor\w+',
    'burlesque',
    u'バーレスク', # japanese burlesque
    'limon',
    'artist\Win\Wresidence',
    'residency',
    'disciplinary',
    'reflective',
    'clogging',
    'zouk',
    u'ズーク', # japanese zouk
    'african dance',
    u'アフリカンダンス', # african dance
    'afro dance',
    'afro mundo',
    'class?ic[ao]',
    'acroyoga',
    'kirtan',
    'hoop\W?dance',
    'modern dance',
    'pilates',
    u'ピラティス', # japanese pilates
    'tribal',
    'jazz', 'tap', 'contemporary',
    u'재즈', # korean jazz
    u'탭 ?댄스', # korean tap dance
    u'súčasný', # contemporary slovak
    u'współczesnego', # contemporary polish
    'contempor\w*', # contemporary italian, french
    'africa\w+',
    'sabar',
    'aerial silk',
    'silk',
    'aerial',
    'zumba',
    'belly\W?danc(?:e(?:rs?)?|ing)', 'bellycraft', 'worldbellydancealliance',
    u'ベリーダンス', # japanese bellydance
    'soca',
    'flamenco',
    'technique',
    'guest artists?',
    'partnering',
    'charleston',
])

# These are okay to see in event descriptions, but we don't want it to be in the event title, or it is too strong for us
DANCE_WRONG_STYLE_TITLE_ONLY = Keyword('DANCE_WRONG_STYLE_TITLE_ONLY', [
    # Sometimes used in studio name even though it's still a hiphop class:
    'ballroom',
    'ballet',
    'yoga',
    'talent shows?', # we don't care about talent shows that offer dance options
    'stiletto',
    '\w+ball', # basketball/baseball/football tryouts
])


#TODO(lambert): we need to remove the empty CONNECTOR here, and probably spaces as well, and handle that in the rules? or just ensure this never gets applied except as part of rules
CONNECTOR = Keyword('CONNECTOR', [
    ' ?',
    ' di ',
    ' de ',
    ' ?: ?',
    u'な', # japanese
    u'の', # japanese
    u'的', # chinese
#TODO(lambert): explore adding these variations, and their impact on quality
#    r' ?[^\w\s] ?',
#    ' \W ',
])

AMBIGUOUS_WRONG_STYLE = Keyword('AMBIGUOUS_WRONG_STYLE', [
    'modern',
    'ballet',
    'ballroom',
])


WRONG_NUMBERED_LIST = Keyword('WRONG_NUMBERED_LIST', [
    'track(?:list(?:ing)?)?',
    'release',
    'download',
    'ep',
])

WRONG_AUDITION = Keyword('WRONG_AUDITION', [
    'sing(?:ers?)?',
    'singing',
    'model',
    'poet(?:ry|s)?',
    'act(?:ors?|ress(?:es)?)?',
    'mike portoghese', # TODO(lambert): When we get bio removal for keyword matches, we can remove this one
])

WRONG_BATTLE = Keyword('WRONG_BATTLE', [
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
    'producer',
])

WRONG_BATTLE_STYLE = Keyword('WRONG_BATTLE_STYLE', [
    '(?:mc|emcee)\Whip\W?hop',
    'emcee',
    'rap',
    'beat',
    'beatbox',
    'dj(?:\W?s)?',
    'producer',
    'performance',
    'graf(?:fiti)?',
])

#TODO: use
# solo performance
# solo battle
# crew battle
# team battle
# these mean....more
#TODO: UNUSED
FORMAT_TYPE = Keyword('FORMAT_TYPE', [
    'solo',
    u'ソロ', # japanese solo
    u'만', # korean solo
    'team',
    u'チーム', # japanese team
    u'팀', # korean team
    'crew',
    u'クルー', # japanese crew
    u'크루', # korean crew
])

BAD_COMPETITION_TITLE_ONLY = Keyword('BAD_COMPETITION_TITLE_ONLY', [
    'video',
    'fundrais\w+',
    'likes?',
    'votes?',
    'votas?', # spanish votes
    u'głosowani\w+', # polish vote
    'support',
    'follow',
    '(?:pre)?sale',
])


VOGUE = Keyword('VOGUE', [
    'butch realness',
    'butch queen',
    'vogue fem',
    'hand performance',
    'face performance',
    'fem(?:me)? queen',
    'sex siren',
    "vou?gue?in[g']?",
    'vou?guin',
    'vou?guer[sz]?',
    'trans\W?man',
    'mini\W?ball',
])
EASY_VOGUE = Keyword('EASY_VOGUE', [
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
    r'f\.?q\.?',
    r'b\.?q\.?',
    'vogue',
    'house of',
    'category',
    'troph(?:y|ies)',
    'old way',
    'new way',
    'ball',
])

SEMI_BAD_DANCE = Keyword('SEMI_BAD_DANCE', [
    'technique',
    'dance company',
    'explore',
    'visual',
    'stage',
    'dance collective',
])

#TODO(lambert): should these be done here, as additional keywords?
# Or should they be done as part of the grammar, that tries to combine these into rules of some sort?

OBVIOUS_BATTLE = Keyword('OBVIOUS_BATTLE', [
    'apache line',
    r'(?:seven|7)\W*(?:to|two|2)\W*(?:smoke|smook|somke)',
])

# TODO(lambert): is it worth having all these here as super-basic keywords? Should we instead just list these directly in rules.py?
BONNIE_AND_CLYDE = Keyword('BONNIE_AND_CLYDE', [
    'bonnie\s*(?:and|&)\s*clyde'
])

KING_OF_THE = Keyword('KING_OF_THE', [
    'king of (?:the )?',
])

KING = Keyword('KING', [
    'king'
])
