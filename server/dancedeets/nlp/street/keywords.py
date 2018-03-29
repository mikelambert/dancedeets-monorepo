# -*-*- encoding: utf-8 -*-*-
#

from dancedeets.nlp import grammar
Any = grammar.Any
Name = grammar.Name

NO_MATCH = grammar.RegexRule('a^')


def GenFileBackedKeywords(name, filename):
    return [Name(name, grammar.FileBackedKeyword(filename, strength=i)) for i in [grammar.STRONG, grammar.STRONG_WEAK]]


BBOY_CREW = GenFileBackedKeywords('BBOY_WORD', 'break/crew*')
BBOY_DANCER = GenFileBackedKeywords('BBOY_DANCER', 'break/dancers*')
CHOREO_CREW = GenFileBackedKeywords('CHOREO_CREW', 'hiphop_choreo/crews*')
CHOREO_DANCER = GenFileBackedKeywords('CHOREO_DANCER', 'hiphop_choreo/dancers*')
FREESTYLE_CREW = GenFileBackedKeywords('FREESTYLE_CREW', 'freestyle/crews*')
FREESTYLE_DANCER = GenFileBackedKeywords('FREESTYLE_DANCER', 'freestyle/dancers*')

CHOREO_KEYWORD = GenFileBackedKeywords('CHOREO_KEYWORD', 'hiphop_choreo/keywords')
FREESTYLE_KEYWORD = GenFileBackedKeywords('FREESTYLE_KEYWORD', 'freestyle/keywords')
COMPETITION = GenFileBackedKeywords('COMPETITION', 'competitions')
GOOD_DJ = GenFileBackedKeywords('GOOD_DJ', 'djs')

BEBOP_CREW = GenFileBackedKeywords('BEBOP_CREW', 'bebop/crews*')
FLEX_KEYWORD = GenFileBackedKeywords('FLEX', 'flex/keywords')

GOOD_INSTANCE_OF_BAD_CLUB = Name(
    'GOOD_INSTANCE_OF_BAD_CLUB', Any(
        'evelyn\W+champagne\W+king',
        'water\W?bottles?',
        'genie in (?:the|a) bottle',
    )
)

BAD_CLUB = Name(
    'BAD_CLUB',
    Any(
        'bottle\W?service',
        'popping?\W?bottles?',
        'bottle\W?popping?',
        'bottles?',
        'grey goose',
        'champagne',
        'belvedere',
        'ciroc',
        'ital zion crew',  # accidentally added one of their private events once.
    )
)

CYPHER = Name(
    'CYPHER',
    Any(
        'c(?:y|i)ph(?:a|ers?)',
        'cyphern',  # german cypher
        u'サイファ',  # japanese cypher
        u'サイファー',  # japanese cypher
        u'サークル',  # japanese circle
        u'サーク',  # japanese circle
        'cerchi',  # italian circle/cypher
        u'ไซเฟอร์',  # thai cypher
        u'싸이퍼.?',  # korean cypher
    )
)

# if somehow has funks, hiphop, and breaks, and house. or 3/4? call it a dance event?

STYLE_POP_WEAK = Any(
    "poppin\'?",
    'boogaloo',
    'gliding',
)
STYLE_HIPHOP_WEAK = Any(
    'hip\W?hop',
    u'хип\W?хоп',
    u'嘻哈',  # chinese hiphop
    u'ההיפ הופ',  # hebrew hiphop
    u'והיפ הופ',  # hebrew hiphop
    u'هيب هوب',  # arabic hiphop
    u'الهيب هوب.',  # arabic 'the hiphop'
    u'хип\W?хоп\w*',  # russian hiphop (хип-хопа)
    u'ヒップホップ',  # hiphop japanese
    u'힙합',  # korean hiphop
    'hip\W?hop\w*',  # lithuanian, polish hiphop
    'hype',
    'new\W?jack\W?swing',
    'old\W?school hip\W?hop',
    '90\W?s hip\W?hop',
    'rnb',
)
STYLE_ALLSTYLE_WEAK = Any(
    'all\W?style[zs]?',
    'tou[ts]\W?style[zs]?',  # french all-styles
    'tutti gli stili',  # italian all-styles
    'kaikille tyyleille avoin',  # finnish all-styles
    u'לכל הסגנונות',  # hebrew all styles
)
STYLE_BREAK_WEAK = Any(
    # 'breaks', # too many false positives
    "breakin[g']?",
    'breakers?',
)
STYLE_DANCEHALL_WEAK = Any(
    'dance\W?hall\w*',
    'ragga',
    u'레게',  # korean reggae
)
STYLE_BEBOP_WEAK = Any('be\W?bop',)

AMBIGUOUS_DANCE_MUSIC = Name(
    'AMBIGUOUS_DANCE_MUSIC',
    Any(
        STYLE_HIPHOP_WEAK,
        STYLE_POP_WEAK,
        STYLE_BREAK_WEAK,
        STYLE_ALLSTYLE_WEAK,
        STYLE_DANCEHALL_WEAK,
        STYLE_BEBOP_WEAK,
        # Starts conflicting with texas city shuffle and shuffle line dances
        #'shuffle',
        'afrobeat',
        'funk',
        'jerk',
        'k\W?pop\w*',
        u'케이팝',  # korean kpop
        u'كي بوب',  # arabic kpop
        'pop',
        'hard\Whitting',
        'electro\W?dance',
        u'얼반',  # korean urban
        'vogue',
    )
)

AMBIGUOUS_DANCE_MUSIC_FULL = Any(
    AMBIGUOUS_DANCE_MUSIC,
    'jazz',
    'samba',
    'latin',
    'blues',
    'country',
)

MUSIC_ONLY = Name(
    'MUSIC_ONLY',
    Any(
        'punk',
        'new wave',
        'rhythm\W?(?:and|&|\+)\W?blues',
        'disco',
        u'диско',  # disco
        'trance',
        u'транс',  # trance
        'techno',
        'techy',
        'alternative',
        'folk',
        'blues',
        'dubstep',
        'bluegrass',
        'electro',
        'electronica',
        'broken beat',
        'dub',
        'europop',
        'pop music',
        'post-punk',
        'trip hop',
        'drum\W?(?:and|&|\+)\W?bass',
        'dnb',
        'd&b',
        'synth\W?pop',
        'breakcore',
        'hardstyle',
        'jumpstyle',
        'progressive',
        'bassline',
        'trap',
        'rap',
        'bossa nova',
        'j\W?pop',
        'c\W?pop',
        'top 40\w?',
        'radio',
        'deep uptempo',
        'elektro',

        # We don't want to add jazz, salsa, etc...as they are also dances,
        # and we don't want to classify these as music (and discard events) because of that
        # r&b is sometimes used for hiphop classes
        # soul is very popular overseas as a dance-related term
        # boogie is very popular as a dancer's name
    )
)

STYLE_BREAK = Name(
    'STYLE_BREAK',
    Any(
        'breakingu',  # breaking polish
        u'breaktánc',  # breakdance hungarian
        u'ブレイク',  # breakdance japanese
        'breakdans',  # breakdance swedish
        "bre?ak\W?dancin[g']?",
        'bre?ak\W?dancer?s?',
        'break\W?danc\w+',
        'power\W?moves?',
        'b\W?(?:boy|girl)\w*',
        u'брейк\W?данс\w*',  # russian breakdance
        u'ברייקדאנס',  # hebrew breakdancing
        u'בברייקדאנס',  # hebrew breakdancing
        u'הברייקדאנס',  # hebrew breakdance
        u'비보이',  # korean bboy
        u'비걸',  # korean bgirl
        u'파워무브',  # powermove korean
        'breakeuse',  # french bgirl
        u'탑락',  # toprock
        u'بريك دانس',  # arabic breakdance
        u'מופעי ברייקדאנס',  # hebrew breakdancing
        u'מקצה ברייקדאנס',  # hebrew breakdancing
        u'ביבוינג',  # hebrew bboying
        u'霹靂舞',  # chinese breakdance
    )
)
# Crazy polish sometimes does lockingu and lockingy. Maybe we need to do this more generally though.
# add(STYLE_BREAK, [x+'u' for x in legit_dance))
STYLE_ROCK = Name('STYLE_ROCK', Any(
    'rock\W?dan[cs]\w+',
    "top\W?rock(?:s|er[sz]?|in[g']?)?",
    "up\W?rock(?:s|er[sz]?|in[g']?|)?",
))
STYLE_POP = Name(
    'STYLE_POP',
    Any(
        'funk\W?style[sz]?',
        'poppers?',
        'popp?i?ng',  # listing poppin in the ambiguous keywords
        'poppeurs?',
        u'паппинг',  # popping
        u'тикинг',  # ticking
        u'вибрация',  # vibrating
        u'анимация',  # animation
        u'крейзи\W?легз',  # crazy legs
        u'быстрая перемотка',  # fast forward
        u'팝핀',  # korean popping
        "pop\W{0,3}(?:(?:N|and|an)\W{1,3})?lock(?:in[g']?|er[sz]?)",  # dupe
        'dubstepp?ing',
        "wavin[g']?",
        'wavers?',
        'liquid\W+dance'
        'liquid\W+(?:\w+\W+)?digitz',
        u'리퀴드댄싱',  # korean liquid dance
        'finger\W+digitz',
        'toy\W?man',
        'puppet\W?style',
        "bott?in[g']?",
        "robott?in[g']?",
        u'로봇팅',  # roboting
        r'\bg\W?styl\w+',
        'strutter[sz]?',
        'strutting',
        u'스트럿팅',  # strutting
        "tuttin[g']?",
        'tutter[sz]?',
        u'텃팅',  # korean tutting
        'poplock\w*',
    )
)
STYLE_LOCK = Name(
    'STYLE_LOCK',
    Any(
        "pop\W{0,3}(?:(?:N|and|an)\W{1,3})?lock(?:in[g']?|er[sz]?)",  # dupe
        "lock(?:er[sz]?|in[g']?)?",
        'lock dance',
        u'локинг',
        u'ロックイング',  # japanese locking (japanese rock/lock is too common)
        u'ロッカーズ',  # japanese lockers
        u'ロッカ',  # japanese lock
        u'락킹',  # korean locking
        'locking4life',
    )
)
STYLE_WAACK = Name(
    'STYLE_WAACK',
    Any(
        "[uw]h?aa?c?c?k(?:er[sz]?|inn?[g']?)",  # waacking
        'waack',
        u'вакинг',  # russian waacking
        u'왁킹',  # korean waacking
        u'ワッキング',  # japanese waacking
        u'パーンキング',  # japanese punking
        "paa?nc?kin[g']?",  # punking
    )
)
STYLE_ALLSTYLE = Name(
    'STYLE_ALLSTYLE',
    Any(
        'mix(?:ed)?\W?style[sz]?',
        'open\W?style[sz]',
        'all\W+open\W?style[sz]?',
        'open\W+all\W?style[sz]?',
        'me against the music',
        'the floor improv night',
    )
)
STYLE_HOUSE = Name(
    'STYLE_HOUSE',
    Any(
        u'хаус',  # russian
        u'浩室舞',
        'houser[sz]?',
        'afro\W?house',
        'dance house',  # seen in italian
    )
)
# This includes anything in the broad class of hiphop dance (mtv, la style, hiphop, hype, etc)
STYLE_HIPHOP = Name(
    'STYLE_HIPHOP',
    Any(
        'mtv\W?style',
        'mtv\W?dance',
        'videoclip\w+',
        'videodance',
        'commercial hip\W?hop',
        'lyrical\Whip\W?hop',
        'hip\W?hop dance',
        'hip\W?hop\Wheels',
        # only do la-style if not salsa? https://www.dancedeets.com/events/admin_edit?event_id=292605290807447
        # 'l\W?a\W?\Wstyle',
        'l\W?a\W?\Wdance',
        'n(?:ew|u)\W?style?\Whip\W?hop',
        u'뉴스타일 ?힙합',  # korean new style hiphop
        'hip\W?hop\Wn(?:ew|u)\W?style?',
        'girl\W?s\W?hip\W?hop',
        'girly\W?hip\W?hop',
        'hip\W?hopp?er[sz]?',
        'video\W?funk',
        'street\W?jazz',
        u'стрит\W?джаз',  # street jazz
        'street\W?funk',
        'jazz\W?funk',
        'funk\W?jazz',
        'boom\W?crack',
        'hype danc\w*',
        'social hip\W?hop',
        'hip\W?hop social dance[sz]',
        'hip\W?hop party dance[sz]',
        'hip\W?hop grooves',
        '(?:new|nu|middle)\W?s(?:ch|k)ool\W\W?hip\W?hop',
        'hip\W?hop\W\W?(?:old|new|nu|middle)\W?s(?:ch|k)ool',
        'newstyleurs?',
    )
)
STYLE_DANCEHALL = Name(
    'STYLE_DANCEHALL',
    Any(
        'ragga\W?jamm?',
        u'댄스 ?레게',  # korean reggae dance
        u'레게 ?댄스',  # korean reggae dance
        u'דאנסהול',  # hebrew dancehall
    )
)
STYLE_KRUMP = Name(
    'STYLE_KRUMP',
    Any(
        'krump',
        "krumpin[g']?",
        'krumper[sz]?',
        u'крамп',  # krump
        u'크럼핑',  # korean krumping
        u'קראמפ',  # hebrew krump
        u'קראמפר',  # hebrew krumper
    )
)
STYLE_TURF = Name('STYLE_TURF', Any(
    "turfin(?:[g']?|er[sz])",
    'turf danc\w+',
))
STYLE_LITEFEET = Name('STYLE_LITEFEET', Any(
    '(?:lite|light)\W?feet\w*',
    "gettin[g']?\W?(?:lite|light)",
))
STYLE_FLEX = Name('STYLE_FLEX', Any(
    "flex(?:in[g']?|er[sz]?)",
    "bone break(?:in[g']?|er[sz]?)",
))
STYLE_BEBOP = Name(
    'STYLE_BEBOP',
    Any(
        'jazz\Wrock',
        u'재즈 ?록',  # korean jazz rock
    )
)
legit_dance = [
    'soulful dance',
    'street\W?jam',
    "jerk(?:ers?|in[g']?)",
    u'스트릿',  # street korean
    u'ストリートダンス',  # japanese streetdance
    u'رقص الشوارع',  # arabic streetdance
    u'البريك دانس',  # arabic breakdance
    u'街舞',  # chinese streetdance / hiphop
    u'街頭舞蹈',  # chinese streetdance
    u'ריקודי רחוב',  # hebrew street dancing
    u'gatvės šokių',  # lithuanian streetdance
    'katutanssi\w*',  # finnish streetdance
    "jookin[g']?",
    "footworkin[g']?",
    u'フットワーキング',  # japanese footworking
    'soul dance',
    u'ソウルダンス',  # soul dance japanese
    #'soul train',...do we want this?
    u'소울트레인',  # korean soul train
    "twerk(?:in[g']?)?",
    u'тверк',  # twerking
    'dance crew[sz]?',
    u'댄스 ?승무원',  # korean dance crew
    'melbourne shuffle',
    'mj\W+style',
    u'майкл джексон стайл',  # michael jackson style
    'michael jackson style',
    'new\W?style hustle',
    'urban danc\w*',
    'urban style[sz]?',
    'urban contemporary',
    u'dan[çc]\w* urban\w*',
    'dan\w+ urbai?n\w+',  # spanish/french urban dance
    'baile urbai?n\w+',  # spanish urban dance
    'estilo\w* urbai?n\w+',  # spanish urban styles
]

# hiphop dance. hiphop dans?
# Crazy polish sometimes does lockingu and lockingy. Maybe we need to do this more generally though.
DANCE = Name('DANCE', Any(*(legit_dance + [x + 'u' for x in legit_dance])))
# TODO(lambert): Is this a safe one to add?
# http://en.wikipedia.org/wiki/Slovak_declension
# dance_keywords = dance_keywords + [x+'y' for x in dance_keywords]

# hiphop dance. hiphop dans?

# house battles https://www.dancedeets.com/events/admin_edit?event_id=240788332653377
HOUSE = Name(
    'HOUSE',
    Any(
        'house',
        u'하우스',  # korean house
        u'ハウス',  # japanese house
        u'хаус',  # russian house
        u'האוס',  # hebrew house
        u'浩室',  # chinese house
    )
)

FREESTYLE = Name(
    'FREESTYLE',
    Any(
        'free\W?style(?:r?|rs?)',
        u'フリースタイル',  # japanese freestyle
        u'فريز ستايل',  # arabic freestyle
        u'פריסטייל',  # hebrew freestyle
    )
)

STREET = Name(
    'STREET',
    Any(
        'street',
        'urban',
        u'уличные',
        u'스트리트',  # korean street
    )
)

JAM = Name(
    'JAM',
    Any(
        'jams?',
        'jamit',  # finnish jams
        u'잼',  # korean jam
    )
)

EASY_CLUB = Any(
    'club',
    u'клубные',  # club
    'klub',
    'after\Wparty',
    'pre\Wparty',
    'party',
    'social',
    u'soirée',
    u'클럽',  # korean club
    u'クラブ',  # japanese club
)
EASY_SESSION = Any(
    'open sessions?',
    u'오픈 ?세션',  # open session
    u'buổi',  # vietnamese sessions
)
EASY_EVENT = Name('EASY_EVENT', Any(
    EASY_CLUB,
    EASY_SESSION,
))

CLUB_ONLY = Name(
    'CLUB_ONLY',
    Any(
        'club',
        'bottle service',
        'table service',
        'coat check',
        # 'rsvp',
        'free before',
        # 'dance floor',
        # 'bar',
        # 'live',
        # 'and up',
        'vip',
        'guest\W?list',
        'drink specials?',
        'resident dj\W?s?',
        'residency',
        'ravers?',
        'techno',
        'trance',
        'indie',
        'glitch',
        'bands?',
        'dress to',
        'mixtape',
        'decks',
        'r&b',
        'local dj\W?s?',
        'all night',
        'lounge',
        'live performances?',
        'doors',  # doors open at x
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
    )
)

POP_MUSIC = Any(
    *[
        '%s\W+pop' for x in
        # List grabbed off wikipedia, but leaving electropop
        [
            'art', 'avant', 'bubble\W+gum', 'chamber', 'country', 'dark', 'dream', 'emo', 'experim\w+', 'folk', 'indie', 'jangle', 'kraut',
            'noise', 'orchest\w+', 'operatic', 'progressive', 'psychedelic', 'surf', 'sunshine', 'swamp', 'teen', 'wonky'
        ]
    ]
)

PREPROCESS_REMOVAL = Name(
    'PREPROCESS_REMOVAL',
    Any(
        'jazz it up',  # usually its the non-jazz things being "jazzed up"
        u'on\W?tap',  # tap dance is definitely not on tap
        u'watch y\w+\W+step',
        u'step\W?(?:by|x)\W?step',
        u'quick\W?step floors',  # it's a cycling team...
        u'baton rouge',  # not a majorette's baton!
        u'gogo inflight',
        u'david gogo',
        u'high performance',  # its not a performance
        u'country club',  # its not country music dance!
        u'marriott international',  # marriott international ballroom, hah
        u'(?:first|second|third)\W?hand',
        u'cha\W?cha\W?s\Wcantina',  # cha cha's cantina
        u'ooh cha cha',  # an event organizer and location
        #
        # french uses 'dans' for 'into' when most other languages use it for 'dance' :(
        u'dans une?',
        u'dans les',
        # positive
        'tap water',  # for theo and dominque's jam
        'house of movement',  # not a vogue keyword!
        'house of dance',  # not a vogue keyword!

        # negative
        "america's got talent",
        'jerk chicken',
        'poker tournaments?',

        # competition
        'fashion competition',
        'wrestling competition',
        't?shirt competition',
        'shaking competition',
        'costume competition',

        # pop
        'bottles? popping?',
        'poppin.? bottles?',
        'pop video',
        'dance fitness',
        'pop\W+music',
        'pop\W*up',
        'eye\W*popping',
        'pearl popping',
        'pony popping',
        'eye-poppin\w+',
        'spinning popping',  # event 1784253371902736 and potentially others
        'pop\W*culture',
        'poppin.?\W?box',
        'cherry popp\w+',
        POP_MUSIC,

        #lock
        'leg\W?lock\w+',

        # refers to ninjitsu stuff, not flexing stuff
        'bone\W*breaking\W+techniques?',

        # Should many of these quality as a "immediate failure" keyword?
        # lock
        'on lock',
        'lock(?:ing|ed|s)? (?:in|out|your|our|the|a|it|down|up)',
        'lock\s*(?:and|\W?n\W?|&)\s*key',
        'lock\s*(?:and|\W?n\W?|&)\s*load',
        'zip\W?lock',
        'lock\Win',
        'lock\W?down',
        'blade\W?lock',
        '(?:through|thru)\W+the\W+lock',
        'lock\W*city\w+',  # event 1886535754903769 and source 311775542225221
        'bike\W?lock',
        'locker\W?room',
        u'ロッカールーム',

        # waack
        'whack music',
        'wack music',
        'wackie\W?s',
        'beat whackz',
        'waking',

        # house
        'power\W?house',
        'at battle house',  # To get rid of most events from 1753270238323171
        'wave\W?house',  # venue in san diego
        'full house',
        'open house',
        'in the house',
        'house band',
        'in\W?house',
        'camp\W?house',
        'hip\W?hop\W?kempu?',  # refers to hiphop music!
        'tiny\W+house',
        'log\W*house',
        'stagehouse',
        'stage\W*house tavern',
        'opera\W?house',

        # extra
        'latin street',
        'marvellous dance crew',
        'johnny soultrain',  # some artist in SF who is named 'soultrain'

        # class
        '1st class',
        'first class',
        'world class',
        'pledge class',
        'world\Wclass',
        'top class',
        'class\W?rnb',
        'class act',
        'class of\W*\d+',
        'of course',

        # stage
        'on stage',
        'main\Wstage',
        'music\Wstage',
        'the stage',
        '(?:second|2nd) stage',

        #break
        'ice\W?break\w+',
        u'アイスブレイク',
        'break down',
        'break(?:ing?)? down',
        'break(?:ing?)? out',
        'ground\W?breaking',
        'board\W?breaking',
        'breaking\W?boards?',
        'record\Wbreaking',
        'break\w+\W+(?:the\W+)?records?',
        'short break',

        # vogue
        'drag on',

        # other
        'go\W?go\W?danc(?:ers?|ing?)',
        'home\W?turf',
        'straight up',  # up rock
        'tear\W?jerker',  # jerker
        'in-strutter',  # strutter
        'juste debout school',
        'baile funk',
        'champs\W+sur',  # french city champs-sur-marne is not a championship event

        # 'step dance' and 'kids classes'
        u'step\W?kids?',
        u'stepping\W?stones?',
    )
)

# battle freestyle ?
# dj battle
# battle royale
# https://www.dancedeets.com/events/admin_edit?event_id=208662995897296
# mc performances
# beatbox performances
# beat
# 'open cyphers'
# freestyle
# in\Whouse  ??
# 'brad houser'

# open mic

# dj.*bboy
# dj.*bgirl

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

# TODO(lambert): use these to filter out shows we don't really care about
# TODO: UNUSED
OTHER_SHOW = Name('OTHER_SHOW', Any(
    'comedy',
    'poetry',
    'poets?',
    'spoken word',
    'painting',
    'juggling',
    'magic',
    'singing',
    'acting',
))

EVENT = Name('EVENT', Any(
    'open circles',
    'abdc',
    'america\W?s best dance crew',
))


def _generate_n_x_n_keywords():
    english_digit_x_keywords = [
        'v/s',
        r'v[zs]?\.?',
        'on',
        'x',
        u'×',  # multiply, sometimes japanese
        u':',
        u'對',  # chinese
        u'על',  # hebrew
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
    n_x_n_keywords += [
        u'%s[ -](?:%s)[ -]%s' % (i, english_digit_x_string, i)
        for i in ['crew', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']
    ]
    return n_x_n_keywords


N_X_N = Name('N_X_N', Any(*_generate_n_x_n_keywords()))

JUDGE = Name(
    'JUDGE',
    Any(
        'jurys?',
        'juryleden',
        'jurados?',  # spanish jury
        u'журито',  # bulgarian jury
        'judge[sz]?',
        u'giám khảo',  # vietnamese judges
        'jures',  # french jury
        '(?:les? )?juges?',  # french judges
        'tuomar(?:it)?',  # finnish judge(s)
        'giudici',  # italian judges
        u'השופט',  # hebrew judge
        u'השופטים',  # hebrew judges
        u'teisėjai',  # lithuanian judges
        'tuomaristo',  # jury finnish
        'jueces',  # spanish judges
        'juriu',  # romanian judges
        'giuria',  # jury italian
        u'評審',  # chinese judges
        u'評判',  # chinese judges
        u'評判團',  # chinese judges
        u'審査員',  # japanese judges
        u'ジャッジ',  # japanese judges
        u'심사',  # korean judges
        u'שופט',  # hebrew judges
        u'השופטים',  # hebrew the-judges
    )
)

AMBIGUOUS_WRONG_STYLE = Name('AMBIGUOUS_WRONG_STYLE', Any(
    'modern',
    'ballet',
    'ballroom',
))

WRONG_NUMBERED_LIST = Name('WRONG_NUMBERED_LIST', Any(
    'track(?:list(?:ing)?)?',
    'release',
    'download',
    'ep',
))

WRONG_AUDITION = Name(
    'WRONG_AUDITION',
    Any(
        'sing(?:ers?)?',
        'singing',
        'model',
        'poet(?:ry|s)?',
        'act(?:ors?|ress(?:es)?)?',
        'mike portoghese',  # TODO(lambert): When we get bio removal for keyword matches, we can remove this one
    )
)

WRONG_BATTLE = Name(
    'WRONG_BATTLE',
    Any(
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
    )
)

WRONG_BATTLE_STYLE = Name(
    'WRONG_BATTLE_STYLE',
    Any(
        '(?:mc|emcee)\Whip\W?hop',
        'emcee',
        'rap',
        'rhyme[sz]',
        'beat',
        'beatbox',
        'dj(?:\W?s)?',
        'producer',
        'performance',
        'graf(?:fiti)?',
    )
)

# TODO: use
# solo performance
# solo battle
# crew battle
# team battle
# these mean....more
# TODO: UNUSED
FORMAT_TYPE = Name(
    'FORMAT_TYPE',
    Any(
        'solo',
        u'ソロ',  # japanese solo
        u'만',  # korean solo
        'team',
        u'チーム',  # japanese team
        u'팀',  # korean team
        'crew',
        u'nhóm',  # vietnamese crew/band
        u'クルー',  # japanese crew
        u'크루',  # korean crew
        u'đội',  # vietnamese team
    )
)

BAD_COMPETITION_TITLE_ONLY = Name(
    'BAD_COMPETITION_TITLE_ONLY',
    Any(
        'video',
        'fundrais\w+',
        'likes?',
        'votes?',
        'votas?',  # spanish votes
        u'głosowani\w+',  # polish vote
        'support',
        'follow',
        '(?:pre)?sale',
    )
)

PRIZE = Name(
    'PRIZE',
    Any(
        'giải thưởng',  # vietnamese prize
    )
)

VOGUE = Name(
    'VOGUE',
    Any(
        u'танцы вог',  # vogue dance
        'butch realness',
        'butch queen',
        'vogue fem',
        'hand performance',
        'face performance',
        u'פרפורמנס',  # hebrew performance
        'fem(?:me)? queen',
        'sex siren',
        "vou?gue?in[g']?",
        'vou?guin',
        'vou?guer[sz]?',
        'trans\W?man',
        'ota face',
        'ota realness',
    )
)

VOGUE_EVENT = Any('mini\W?ball',)

# We want to ignore these when trying to match against house events (r'\bhouse\b')
# But at the same time, we want to include them when trying to match against vogue events (r'\bhouse of\b')
HOUSE_OF = Name('HOUSE_OF', Any('house of',))

TOO_EASY_VOGUE = Name('TOO_EASY_VOGUE', Any(
    'open to all',
    'troph(?:y|ies)',
))

EASY_VOGUE = Name(
    'EASY_VOGUE',
    Any(
        HOUSE_OF,
        'never walked',
        'virgin',
        'drags?',
        # twist-o-flex
        # 'twist',
        'realness',
        'runway',
        'female figure',
        'couture',
        'butch',
        'ota',
        r'f\.?q\.?',
        r'b\.?q\.?',
        'vogue',
        u'вог',
        'old way',
        'new way',
        'ball',
    )
)

WRONG_LOCK = Name(
    'WRONG_LOCK',
    Any(
        'mma',
        'jiu\W?jitsu',
        'leg',
        'grappl\w+',
        'picking',
        'cracking',
        'crack',
        'pick',
        'key',
        'boaters?',
        'the locks',
        'marina',
        'dam',
        'vessel',
        'bind',
        'blade',
        'dialog',
        'needlework',
        'embroider\w+',
    )
)

WRONG_HOUSE = Name('WRONG_HOUSE', Any(
    'walls?',
    'windows?',
    'roofs?',
    'logs?',
    'tile[sd]?',
    'kitchen',
    'houses',
))

WRONG_POP = Any(
    'popstar',
    'concert',
    'idol',
)

WRONG_BREAK = Name(
    'WRONG_BREAK',
    Any(
        'horses?',  # breaking in horses
    )
)

WRONG_FLEX = Name('WRONG_FLEX', Any(
    'ninjutsu',
    'jutsu',
    'pressure point',
))

SEMI_BAD_DANCE = Name('SEMI_BAD_DANCE', Any(
    'technique',
    'dance company',
    'explore',
    'visual',
    'stage',
    'dance collective',
))

# TODO(lambert): should these be done here, as additional keywords?
# Or should they be done as part of the grammar, that tries to combine these into rules of some sort?

OBVIOUS_BATTLE = Name('OBVIOUS_BATTLE', Any(
    'apache line',
    r'(?:seven|7)\W*(?:to|two|2)\W*(?:smoke|smook|somke)',
))

# TODO(lambert): is it worth having all these here as super-basic keywords? Should we instead just list these directly in rules.py?
BONNIE_AND_CLYDE = Name('BONNIE_AND_CLYDE', Any('bonnie\s*(?:and|&)\s*clyde' 'jack\s*(?:and|&)\s*jill',))

KING_OF_THE = Name('KING_OF_THE', Any('king of (?:the )?',))

KING = Name('KING', Any('king'))
