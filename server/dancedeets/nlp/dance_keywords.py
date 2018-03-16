# -*-*- encoding: utf-8 -*-*-
#

from dancedeets.nlp import grammar
Any = grammar.Any
Name = grammar.Name

MUSIC = Any(
    u'awit',  # tagalog
    u'bài hát',  # vietnamese, vietnamese
    u'canciones',  # spanish
    u'canción',  # spanish
    u'canzone',  # italian
    u'canzoni',  # italian
    u'canção',  # portuguese
    u'chanson',  # french
    u'chansons',  # french
    u'cântec',  # romanian
    u'cântece',  # romanian
    u'daina',  # lithuanian
    u'dainos',  # lithuanian
    u'dal',  # hungarian
    u'dalok',  # hungarian
    u'glazba, muzika',  # croatian
    u'hudba',  # czech
    u'hudební',  # czech
    u'kanta',  # tagalog
    u'lagu',  # malay
    u'lagu-lagu',  # malay
    u'laulu',  # finnish
    u'lauluja',  # finnish
    u'lied',  # dutch, german
    u'lieder',  # german
    u'låt',  # swedish
    u'låtar',  # swedish
    u'mjuzikl',  # croatian
    u'm[uúü][sz]i[ie]?[ckq]\w*',
    u'muzyka',  # polish
    u'piosenk\w+',  # polish
    u'pjesm\w+',  # croatian
    u'píseň',  # czech
    u'písně',  # czech
    u'sang',  # danish, norwegian
    u'sange',  # danish
    u'sanger',  # norwegian
    u'song',  # english
    u'songs',  # dutch, english
    u'zene',  # hungarian
    u'zenei',  # hungarian
    u'âm nhạc',  # vietnamese
    u'şarkı',  # turkish
    u'şarkılar',  # turkish
    u'μιούζικαλ',  # greek
    u'μουσικα κομματια',  # greek
    u'μουσικη',  # greek
    u'τραγούδι',  # greek
    u'музич?к\w+',  # macedonian
    u'музыка\w*',  # russian
    u'песн\w+',  # macedonian
    u'מוּסִיקָה',  # hebrew
    u'מוּסִיקָלִי',  # hebrew
    u'שִׁיר',  # hebrew
    u'שירים',  # hebrew
    u'أغنية',  # arabic
    u'الأغاني',  # arabic
    u'موسيقى',  # arabic
    u'موسيقي',  # arabic
    u'ดนตรี',  # thai
    u'เพลง',  # thai, thai, thai
    u'ミュージカル',  # japanese
    u'曲',  # japanese
    u'歌',  # japanese
    u'歌曲',  # chinese simplified, chinese simplified, chinese traditional, chinese traditional
    u'音乐',  # chinese simplified
    u'音乐',  # chinese simplified
    u'音楽',  # japanese
    u'音樂',  # chinese traditio
    u'音樂',  # chinese traditional
    u'노래',  # korean
    u'노래들',  # korean
    u'음악',  # korean
)

# Can we generate this automatically from two params?
dance_not_dancehall = Any(
    # 'dance\w*' minus 'dancehall'
    u'dance',
    u'dance[^h\W]\w*',
    u'danceh',
    u'danceh[^a\W]\w*',
    u'danceha',
    u'danceha[^l\W]\w*',
    u'dancehal',
    u'dancehal[^l\W]\w*',
)
# 'crew' biases dance one way, 'company' biases it another
EASY_DANCE = Name(
    'EASY_DANCE',
    Any(
        u'baila\w*',  # spanish
        u'baile',  # spanish
        u'baile[^y]\w*',  # spanish (avoid baileys)
        u'ballerin[io]s?',  # dancer italian
        u'ballano',  # dance italian
        u'ballem',  # dance catalan
        u'dancer?s?',  # english
        dance_not_dancehall,
        u'dance style[sz]',
        u"dancin[g']?",
        u'dansles',
        u'dans[aeç]\w*',
        u'danse\w*',  # french and danish
        u'dansa\w*',  # dance-* swedish
        u'dansı\w*',  # turkish
        u'dansul\w*',  # dance romanian
        u'dansgolv',  # dance floor swedish
        u'dans',  # let the above, try to match first!
        u'danza\w*',  # dance italian
        u'danç\w*',  # dance/dancers portuguese
        u'điệu nhảy',  # vietnamese
        u'khiêu vũ',  # vietnamese
        u'mananayaw',  # tagalog
        u'menari',  #  malay
        u'múa',  # dance vietnamese
        u'nhảy',  # vietnamese
        u'penari',  #  malay
        u'plesa',  # dance croatian
        u'plesu',  # dancing croatian
        u'plešete',  # dancing croatian
        u'sayaw\w*',  # tagalog
        u'social\W?dance',
        u'tancerz',  # polish
        u'tane?[cč]\w*',  # czech
        u'tańe?c\w*',  # dance polish/czech
        u'taniec',  # polish
        u'tanssi\w*',  # finnish
        u'tanzen',  # german
        u'tarian',  # malay
        u'tánc\w*',  # hungarian
        u't[aä]nz\w*',  # german
        u'vũ công',  # vietnamese
        u'vũ đạo',  # dance vietnamese
        u'zaplešite',  # dance croatian
        u'zatanč\w*',  # dance czech
        u'šok\w*',  # dance lithuanian
        u'χορ[όέ]\w*',  # greek dance/choreography
        u'тане?ц\w*',  # russian
        u'танчер\w*',  # dancer macedonian
        u'изтанц\w*',  # russian/bulgarian dance
        u'לִרְקוֹד',  # hebrew
        u'רַקדָן',  # hebrew
        u'ריקוד',  # hebrew
        u'בלרקוד',  # hebrew dancing
        u'רקוד',  # hebrew dancing
        u'כשרוקדים',  # hebrew 'when dancing'
        u'ריקודים',  # hebrew dances
        u'ריקודי',  # hebrew dance
        u'רוקד',  # hebrew dance
        u'רוקדים',  # hebrew dance
        u'רקדם',  # hebrew dancers
        u'הריקוד',  # hebrew dance
        u'רקדנים',  # hebrew dancers
        u'לרקדני',  # hebrew dancers
        u'לרקדנים?',  # hebrew 'for the dancers'
        u'רקדן',  # hebrew dancer
        u'راقصة?',  # arabic
        u'دانس',  # arabic dance transliteration
        u'رقص',  # arabic
        u'رقصة',  # arabic
        u'الرقص',  # arabic
        u'แดนซ์',  # dance thai
        u'(?:การ)?(?:ลีลาศ|ฟ้อนรำ|ร่ายรำ|เริงระบำ|ก?เต้น\w*)',  # thai
        u'ダンサー',  # japanese
        u'ダンシング',  # japanese
        u'ダンス',  # japanese
        u'踊り',  # japanese dance
        u'舞者',  # chinese dancer
        u'舞技',  # chinese dancing
        u'舞.?蹈',  # chinese dance
        u'舞',  # chinese dance
        u'排舞',  # chinese dance
        u'蹈',  # chinese dance
        u'跳.?舞',  # chinese dance
        u'댄스',  # korean
        u'댄서',  # korean dancer
        u'춤추는?',  # korean
        u'नृत्य',  # hindi dance
        u'ダンサー',  # japanese dance
        u'ダンス',  # japanese dance
        u'踊',  # japanese dance prefix
        u'춤.?',  # korean dance
        u'추고.?.?',  # korean dancing
        u'댄서.?.?',  # korean dancers
        u'무용',
        u'footwork',
    )
)

EASY_CHOREO = Name(
    'EASY_CHOREO',
    Any(
        u'biên đạo(?: múa)?',  # vietnamese
        u'(?:c|ch|k)oreo',
        u'(?:c|ch|k)or(?:eo|eó|é)gr[aá]\w+',
        u'chorée',  # french choreo
        u'kareogra\w+',  # turkish
        u'χορογρ\+',  # greek
        u'кореограф\w*',  # macedonian
        u'хорео\w*',  # macedonian/russian
        u'балетмейстерски\w*',  # russain choreography (ballet master)
        u'χορογραφια\w*',
        u'כּוֹרֵיאוֹגר\w*',  # hebrew
        u'مدير الرقص',  # arabic
        u'นัก|การออกแบบท่าเต้น',  # thai
        u'ท่าเต้น',  # thai
        u'ออกแบบท่าเต้น',  # thai
        u'振り付け',  # japanese
        u'振付師',  # japanese
        u'編舞',  # chinese traditional
        u'编舞',  # chinese simplified
        u'排舞',  # chinese choreography/formation
        u'안무가?',  # korean
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
    u'alkeet',  # finnish basic
    u'alkeisjatko',  # finnish beginners
)
_ALL_LEVELS = Any(
    'all',
    'mixed',
    'open',
)
_INTRODUCTION = Any(
    u'basics',
    u'intro(?:duction)? to',
    u'iniciação ao',  # portuguese
    u'introducción a',  # spanish
    u'introduction à',  # french
    u'introduzione a',  # italian
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
    u'dersi',  # turkish lesson
    u'unterricht',  # german lessons
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
    u'(?:спец)?курс',  # russian course
    u'семинар',  # russian seminar
    'class(?:es)?',
    'lessons?',
    'lessens?',
    'dansles',  # dance lesson
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
    u'cursuri\w*',  # course romanian
    'tanzanleitung',  # dance-instruction german
    'anleitung',  # guidance/instruction german
    'kur[sz](?:y|en)?',  # course german/polish/czech
    'aulas?',  # portuguese class(?:es)?
    u'특강',  # korean lecture
    'lektion(?:en)?',  # german lecture
    'lekcie',  # slovak lessons
    'dansklasser',  # swedish dance classes
    u'(?:nybörjar|introduktions|fördjupnings)(?:kurs|klass)(?:er)?',  # swedish beginners/intro/advanced course/class singular/plural
    'lekcj[ai]',  # polish lesson
    'eigoje',  # lithuanian course
    u'pamokas?',  # lithuanian lesson
    u'pamokėlės?',  # lithuanian lessons
    'kursai',  # course lithuanian
    'kursas',  # course lithuanian
    'kurs',  # course dutch
    u'kurssin?',  # course finnish
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
        grammar.connected(Any(EASY_DANCE, EASY_CHOREO), CLASS_ONLY),
        _CLASS_LEVELS,
        grammar.connected(CLASS_ONLY, Any('in')),
        #WITH,
        grammar.commutative_connected(CLASS_ONLY, Any(FREE, _CLASS_LEVELS, WITH)),
    )
)
SPANISH_CLASS = Any(
    u'taller',
    u'talleres',
)

ROMANCE_LANGUAGE_CLASS = Name('ROMANCE_LANGUAGE_CLASS', Any(
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
        'danskamp',
    )
)

AUDITION_ONLY = Any(
    u'audicija\s*',  # croatian
    u'audi[tc]i[óo]n\s*',  # spanish
    u'auditie\w*',  # dutch
    u'audição\w*',  # portuguese
    u'esiintymiskoe',  # finnish
    u'işitme',  # turkish
    u'klausymasis',  # lithuanian
    u'konkur[sz]',  # czech
    u'meghallgatás',  # hungarian
    u'provino',  # italian
    u'przesłuchanie',  # polish
    u'thử vai',  # vietnamese
    u'uji bakat',  # malay
    u'vorsprechen',  # german
    u'ακοή',  # greek
    u'аудиција',  # macedonian
    u'прослушивание',  # russian
    u'אודישן',  # hebrew
    u'الاختبار',  # arabic
    u'การได้ยิน',  # thai
    u'オーディション',  # japanese
    u'面試',  # chinese traditional
    u'面试',  # chinese simplified
    u'試鏡',  # chinese traditional
    u'试音',  # chinese simplfiied
    u'오디션',  # korean
)

AUDITION = Name(
    'AUDITION',
    Any(
        AUDITION_ONLY,
        'try\W?outs?',
        'casting',
        'castingi',  # polish casting
        'casting call',
        'castingul',  # romanian casting
        u'トライアウト',  # japanese tryout
        'audizion\w*',  # italian audition
        'naborem',  # polish recruitment/audition
        'sign\W?ups',
        'rehearsal',
        u'綵排',  # chinese rehearsal
    )
)

CONTEST = Name(
    'CONTEST',
    Any(
        u'conc(?:o|u|ou)rs\w*',  # portuguese
        u'contests?',  # norwegian
        u'cuộc thi',  # vietnamese
        u'des concours',  # french
        u'kilpailu\w*',  # finnish
        u'konkurr[ae]n[cs]e\w*',  # danish, norwegian
        u'konkurs\w*',  # lithuanian, polish
        u'mga paligsahan',  # tagalog
        u'natjecanj\w*',  # croatian
        u'paligsahan',  # tagalog
        u'pertandingan',  # malay
        u'soutěž\w*',  # czech
        u'tävling\w*',  # swedish
        u'verseny\w*',  # hungarian
        u'wedstrijd\w*',  # dutch
        u'wettbewerb\w*',  # german
        u'yarışma\w*',  # turkish
        u'zawody',  # polish
        u'διαγωνισμο\w*',  # greek
        u'конкурс\w*',  # russian
        u'натпревар\w*',  # macedonian
        u'תַחֲרוּת',  # hebrew
        u'תחרויות',  # hebrew
        u'مسابق\w*',  # arabic
        u'การประกวด',  # thai
        u'การแข่งขัน',  # thai
        u'コンクール',  # japanese contest
        u'コンテスト',  # japanese
        u'比賽',  # chinese traditional
        u'比赛',  # chinese simplified
        u'竞赛',  # chinese simplified
        u'競賽',  # chinese traditional
        u'경연',  # korean
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

#TODO: Add recitals. dansrecital

PERFORMANCE = Name(
    'PERFORMANCE',
    Any(
        'shows?',
        'spectacle',
        'performances?',
        'festival',
        'show\W?case',
        'encontro',  # portuguese meeting/festival
        u'esibiziones?',  # italian performance
        u'représentation',  # french performance
        'espectaculo',  # spanish performance
        u'espectáculo',  # spanish performance
        u'퍼포먼스',  # korean performance
        u'쇼케이스',  # korean showcase
        u'공연',  # korean performance
        u'공연이',  # korean performance
        u'ショーケース',  # japanese showcase
        u'成果發表會',  # chinese 'result presentation' (final performance)
        u'秀',  # chinese show
        u'公演',  # chinese performance
        u'展',  # chinese exhibition/show
        u'果展',  # chinese exhibition
        u'表演',  # chinese performance
        u'спектакль',  # russian performance
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
