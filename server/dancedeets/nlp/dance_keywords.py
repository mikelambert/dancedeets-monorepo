# -*-*- encoding: utf-8 -*-*-
#

from dancedeets.nlp import grammar
Any = grammar.Any
Name = grammar.Name

# 'crew' biases dance one way, 'company' biases it another
EASY_DANCE = Name(
    'EASY_DANCE',
    Any(
        'dances?',
        "dancin[g']?",
        'dancers?',
        'dance\w+',
        'dance style[sz]',
        'social\W?dance',
        u'χορ[όέ]\w*',  # greek dance/choreography
        u'رقص',  # arabic dance native
        u'دانس',  # arabic dance transliteration
        u'नृत्य',  # hindi dance
        u'댄스',  # korean dance
        u'댄서',  # korean dancer
        u'танц\w*',  # russian/bulgarian dance
        u'изтанц\w*',  # russian/bulgarian dance
        u'רקוד',  # hebrew dancing
        u'בלרקוד',  # hebrew dancing
        u'כשרוקדים',  # hebrew 'when dancing'
        u'ריקודים',  # hebrew dances
        u'ריקודי',  # hebrew dance
        u'ダンサー',  # japanese dance
        u'ダンス',  # japanese dance
        u'踊',  # japanese dance prefix
        u'춤.?',  # korean dance
        u'추고.?.?',  # korean dancing
        u'댄서.?.?',  # korean dancers
        u'踊り',  # japanese dance
        u'רוקד',  # hebrew dance
        u'רקדם',  # hebrew dancers
        u'הריקוד',  # hebrew dance
        u'רוקדים',  # hebrew dance
        u'רקדנים',  # hebrew dancers
        u'לרקדני',  # hebrew dancers
        u'לרקדנים',  # hebrew 'for the dancers'
        u'רקדן',  # hebrew dancer
        u'ריקוד',  # hebrew dance
        u'舞者',  # chinese dancer
        u'舞技',  # chinese dancing
        u'舞.?蹈',  # chinese dance
        u'舞',  # chinese dance
        u'排舞',  # chinese dance
        u'蹈',  # chinese dance
        u'跳.?舞',  # chinese dance
        u'แดนซ์',  # dance thai
        u'เต้น',  # dance thai
        u'กเต้น',  # dancers thai
        u'nhảy',  # dance vietnamese
        u'vũ đạo',  # dance vietnamese
        u'múa',  # dance vietnamese
        'danse\w*',  # french and danish
        'taniec',  # dance polish
        u'tane?[cč][íú\w]*',  # dance slovak/czech
        u'zatanč\w*',  # dance czech
        u'tańe?c\w*',  # dance polish/czech
        u'danç\w*',  # dance/dancers portuguese
        'danza\w*',  # dance italian
        u'šok\w*',  # dance lithuanian
        'tanz\w*',  # dance german
        u'tänz\w*',  # dance german
        'tanssi\w*',  # finnish dance
        'bail[ae]\w*',  # dance spanish
        'danzas',  # dance spanish
        'ballerin[io]',  # dancer italian
        'ballano',  # dance italian
        'ballem',  # dance catalan
        'dansare',  # dancers swedish
        'dansat',  # dancing swedish
        'dansama',  # dancers swedish
        'dansa\w*',  # dance-* swedish
        'dansgolv',  # dance floor swedish
        'dans',  # swedish danish dance
        u'tänzern',  # dancer german
        u'танчер',  # dancer macedonian
        u'танцовиот',  # dance macedonian
        'footwork',
        'plesa',  # dance croatian
        'plesu',  # dancing croatian
        u'plešete',  # dancing croatian
        u'zaplešite',  # dance croatian
        u'nhảy',  # dance vietnamese
        u'tänzer',  # dancer german
    )
)

EASY_CHOREO = Name(
    'EASY_CHOREO',
    Any(
        u'(?:ch|k|c)oe?re[o|ó]?gr[aá](?:ph|f)\w*',  # english, italian, finnish, swedish, german, lithuanian, polish, italian, spanish, portuguese, danish
        'choreo',
        u'chorée',  # french choreo
        u'chorégraph\w*',  # french choreographer
        u'biên đạo',  # vietnamese choreography
        u'кореограф',  # macedonian
        u'안무',
        u'χορογραφια\w*',
    )
)

BATTLE = Name(
    'BATTLE',
    Any(
        'battle of the year',
        'boty',
        'compete',
        'competitions?',
        'konkurrence',  # danish competition
        'competencia',  # spanish competition
        u'competición',  # spanish competition
        u'compétition',  # french competition
        u'thi nhảy',  # dance competition vietnam
        'kilpailu\w*',  # finish competition
        'konkursams',  # lithuanian competition
        'verseny',  # hungarian competition
        'championships?',
        'champs?',
        u'dự thi',  # vietnamese competition
        u'phần thi',  # vietnamese competition
        u'giải đấu',  # vietnamese tournament
        u'thi đấu',  # competition vietnamese
        u'čempionatams',  # lithuanian championship
        'campeonato',  # spanish championship
        'meisterschaft',  # german championship
        'concorsi',  # italian competition
        u'danstävling',  # swedish dance competition
        u'แข่งขัน',  # thai competition
        u'대회에서',  # korean competition
        u'선수권대회',  # korean champsionship
        u'대회',  # korean rally/tournament/etc commonality
        u'대전',  # korean battle
        u'배틀',  # korean battle
        'crew battle[sz]?',
        'exhibition battle[sz]?',
        'battle[ts]?',
        'battlu(?:je)?',  # french czech
        'batalhas?',  # portuguese battles
        u'competiç\w+',  # portuguese competitions
        u'大賽',  # chinese competition
        u'比賽',  # chinese battle
        u'賽',  # chinese race/competition/etc
        u'交流賽',  # chinese battle exchange
        u'バトル',  # japanese battle
        u'битката',  # bulgarian battle
        'batallas',  # battles spanish
        'zawody',  # polish battle/contest
        'walki',  # polish battle/fight
        u'walkę',  # polish battle/fight
        'bitwa',  # polish battle
        u'bitwę',  # polish battle
        'bitwach',  # polish battle
        u'バトル',  # japanese battle
        'tournaments?',
        'tournoi',  # french tournament
        u'大会',  # japanese tournament
        u'トーナメント',  # japanese tournament
        'turnie\w*',  # tournament polish/german
        u'състезанието',  # competition bulgarian
        u'đấu',  # game vietnamese
        'turneringer',  # danish tournament
        'preselections?',
        u'présélections?',  # preselections french
        'prelims?',
        u'初賽',  # chinese preliminaries
        u'קרבות',  # hebrew battle
        u'منافسات',  # arabic competitions
        u'مسابقات',  # arabic contests
        u'معركة',  # arabic battle
        u'התחרות',  # hebrew competition
        u'לתחרות',  # hebrew competition
        u'לאליפות',  # hebrew championship
        u'אליפות',  # hebrew championship
        u'באליפות',  # hebrew championship
        u'לקרבות',  # hebrew battles
        u'תחרות',  # hebrew competition
        'queen',  # dancehall competition
    )
)

_LEVEL = Any(
    'levels?',
    u'レベル',
    u'水平',
    'niveau',
    'nivel',
    'livello',
)
_ACTUAL_LEVELS = Any(
    'beg(?:inners?|inning|\.)?',
    'int(?:ermediates?|\.)?',
    'medel\w*',  # swedish
    'adv(?:anced|\.)?',
    'avancerad',  # swedish
    #triggers on hiphop master, funk master
    #'master',
    'professional',
    'adults?',
    'kids?',
    u'初心者?',
)
_ALL_LEVELS = Any(
    'all',
    'mixed',
    'open',
)
_INTRODUCTION = Any(
    'intro(?:duction)? to',
    u'iniciação ao',  # portuguese
    u'introducción a',  # spanish
    u'introduction à',  # french
    'introduzione a',  # italian
    u'einführung zu',  # german
    u'紹介',  # japanese
    u'介紹',  # chinese
    u'소개',  # korean
)
_CLASS_LEVELS = Any(
    _INTRODUCTION,
    grammar.connected(_LEVEL, grammar.RegexRule('[12345]')),
    _ACTUAL_LEVELS,
    grammar.commutative_connected(_ACTUAL_LEVELS, _ALL_LEVELS),
    grammar.commutative_connected(_ACTUAL_LEVELS, _ACTUAL_LEVELS),
    grammar.commutative_connected(_ACTUAL_LEVELS, _LEVEL),
)

WITH = Name(
    'WITH',
    Any(
        'with',
        'avec',  # french
        'con',  # spanish, italian
        'mit',  # german
        'ja',  # finish
        u'同',
        u'跟',
        u'と',
        u'와',
    )
)

CLASS_ONLY = Any(
    'work\W?shop(?:\W?s|\w+)?',
    'ws',  # japanese workshop WS
    'w\.s\.',  # japanese workshop W.S.
    u'ワークショップ',  # japanese workshop
    u'작업장',  # korean workshop
    u'סדנת',  # hebrew workshop
    u'בסדנה',  # hebrew workshop
    u'בסדנא',  # hebrew workshop
    u'הקורס',  # hebrew course
    u'hội thảo',  # vietnamese workshop
    'cursillo',  # spanish workshop
    'ateliers?',  # french workshop
    'workshopy',  # czech workshop
    u'סדנאות',  # hebrew workshops
    u'סדנה',  # hebew workshop
    u'הסדנא',  # hebrew workshop
    u'שיעורים',  # hebrew lessons
    u'μάθημα',  # greek lesson
    u'σεμιναριο',  # greek seminar
    # 'taller', # workshop spanish
    'delavnice',  # workshop slovak
    'talleres',  # workshops spanish
    'radionicama',  # workshop croatian
    u'časovi',  # class croatian
    'warsztaty',  # polish workshop
    u'warsztatów',  # polish workshop
    u'nauka',  # polish instructional
    u'uczyli',  # polish teaching
    u'seminarų',  # lithuanian workshop
    'taller de',  # spanish workshop
    'workshoppien',  # finnish workshops
    'intensives?',
    'intensivo',  # spanish intensive
    'open class.?',
    'master\W?class(?:es)?',
    'company class',
    u'мастер\W?класса?',  # russian master class
    u'класса?',  # russian class (this is not a normal 'a')
    'class(?:es)?',
    'lessons?',
    'courses?',
    # TODO: should i do a "class(?!ic)"
    'klass(?:en)?',  # slovakian class
    u'수업',  # korean class
    u'수업을',  # korean classes
    'lekc[ie]',  # czech lesson
    u'課程',  # course chinese
    u'課',  # class chinese
    u'堂課',  # lesson chinese
    u'表演班',  # performance class
    u'專攻班',  # chinese specialized class
    u'工作坊',  # chinese workshop/lab
    u'コース',  # course japanese
    u'交流会',  # exchange meeting japanese
    'cors[io]',  # course italian
    'concorso',  # course italian
    'concurso',  # course spanish
    'cursuri',  # course romanian
    'tanzanleitung',  # dance-instruction german
    'anleitung',  # guidance/instruction german
    'kur[sz](?:y|en)?',  # course german/polish/czech
    'aulas?',  # portuguese class(?:es)?
    u'특강',  # korean lecture
    'lektion(?:en)?',  # german lecture
    'lekcie',  # slovak lessons
    'dansklasser',  # swedish dance classes
    'lekcj[ai]',  # polish lesson
    'eigoje',  # lithuanian course
    'pamokas',  # lithuanian lesson
    'kursai',  # course lithuanian
    'kursas',  # course lithuanian
    'kurs',  # course dutch
    'choreokurs\w*',  # choreo course dutch
    'lez\.',  # lesson italian
    'lezion[ei]?',  # lesson italian
    u'zajęciach',  # class polish
    u'zajęcia',  # classes polish
    u'คลาส',  # class thai
    'classe',  # class italian
    'classi',  # classes italin
    'klasser?',  # norwegian class
    'cours',
    'clases?',
    'formazione',  # training italian
    'formazioni',  # training italian
    u'トレーニング',  # japanese training
    'teach(?:ing?|ers?)',
)
FREE = Any(
    'free',
    'kostenlose',  # german
    'grat\w+',  # latin/romance languages
    u'無料',  # japanese
    u'免費',  # chinese
    u'무료',  # kroean
)
CLASS = Name(
    'CLASS',
    Any(
        CLASS_ONLY,
        _CLASS_LEVELS,
        grammar.connected(CLASS_ONLY, Any('in')),
        #WITH,
        grammar.commutative_connected(CLASS_ONLY, Any(FREE, _CLASS_LEVELS, WITH)),
    )
)

ROMANCE_LANGUAGE_CLASS = Name('ROMANCE_LANGUAGE_CLASS', Any(
    'spectacle',
    'stage',
    'stages',
))

# Used to be in classes, but have disabled these due to false positives
_CAMP = Name(
    'CAMP',
    Any(
        'camp',
        'kamp',
        'kemp',
        u'캠프',  # korean camp
        u'營',  # chinese camp
    )
)

AUDITION = Name(
    'AUDITION',
    Any(
        'try\W?outs?',
        'casting',
        'castingi',  # polish casting
        'casting call',
        'castingul',  # romanian casting
        'auditions?',
        'audicija',  # audition croatia
        'audiciones',  # spanish audition
        'konkurz',  # audition czech
        u'オーディション',  # japanese audition
        u'トライアウト',  # japanese tryout
        u'試鏡',  # chinese audition
        u'오디션',  # korean audition
        'audizione',  # italian audition
        'naborem',  # polish recruitment/audition
        'rehearsal',
        u'綵排',  # chinese rehearsal
    )
)

CONTEST = Name(
    'CONTEST',
    Any(
        'contests?',
        'concours',  # french contest
        'konkurrencer',  # danish contest
        'konkuranser',  # norwegian contest/competition
        'dancecontests',  # dance contests german
    )
)
PRACTICE = Name(
    'PRACTICE',
    Any(
        'sesja',  # polish session
        'practice',
        'session',  # the plural 'sessions' is handled up above under club-and-event keywords
        u'セッション',  # japanese session
        u'練習会',  # japanese training
        u'練習',  # japanese practice
        u'연습',  # korean practice/runthrough
    )
)

PERFORMANCE = Name(
    'PERFORMANCE',
    Any(
        'shows?',
        'performances?',
        'festival',
        'show\W?case',
        'encontro',  # portuguese meeting/festival
        u'représentation',  # french performance
        'espectaculo',  # spanish performance
        u'espectáculo',  # spanish performance
        u'퍼포먼스',  # korean performance
        u'쇼케이스',  # korean showcase
        u'ショーケース',  # japanese showcase
        u'成果發表會',  # chinese 'result presentation' (final performance)
        u'秀',  # chinese show
        u'公演',  # chinese performance
        u'展',  # chinese exhibition/show
        u'果展',  # chinese exhibition
        u'表演',  # chinese performance
        u'biểu diễn',  # vietnamese performance
        u'trình diễn',  # vietnamese performance
        u'vystoupení',  # czech performances
        u'výkonnostních',  # czech performance
        u'wykonaniu',  # polish performance
        u'изпълнението',  # bulgarian performance
        u'パフォーマンス',  # japanese performance
        u'מופע',  # hebrew show/performance
        u'מופעי',  # hebrew show/performance
        u'למופע',  # hebrew 'for the show'
        u'ראווה',  # hebrew show/showcase
        # maybe include 'spectacle' as well?
        'esibizioni',  # italian performance/exhibition
    )
)

ROMANCE = Name(
    'ROMANCE',
    Any(
        'di',
        'i',
        'e',
        'con',  # italian
        "l'\w*",
        'le',
        'et',
        'une',
        'avec',
        u'à',
        'pour',  # french
    )
)

KIDS = Name(
    'KIDS',
    Any(
        'kid\W?s?',
        'child(?:ren)?\W?s?',
        'students?',
        'high\W?school',
        'college',
        'university',
        'under\W?\d+',
        u'キッズ',  # japanese kids
        u'子供',  # japanese kids
        u'学生',  # japanese students
        u'高校',  # japanese high school
        u'カレッジ',  # japanese college
        u'大学',  # japanese university
        u'歳以下',  # japanese/chinese under-age
        u'孩子們?',  # chinese kids
        u'兒童',  # chinese child
        u'學生們?',  # chinese students
        u'中學',  # chinese high school
        u'學院',  # chinese college
        u'大學',  # chinese university
        u'아이들',  # korean kids
        u'어린이',  # korean kids
        u'재?학생',  # korean students
        u'고등학교',  # korean high school
        u'칼리지',  # korean college
        u'대학',  # korean university
        u'세 미만',  # korean under-age
        'enfants?',  # french kids
        u'étudiant',  # french students
        u'élèves',  # french students
        u'école secondaire',  # french high school
        u'université',  # french college/university
        u'moins de\W?\d+\W?ans',  # french under-age
        'ragazz[io]',  # italian kid
        'bambin[io]',  # italian kids
        'alunn[io]',  # italian student
        'student[io]',  # italian student
        'scuola superiore',  # italian high school
        u'università',  # italian university
        'sotto i\W?\d+',  # italian under-age
        'kinderen',  # dutch children
        'tot \d+ jaar',  # dutch to-n-years
        'dzieci\w*',  # polish children
    )
)
