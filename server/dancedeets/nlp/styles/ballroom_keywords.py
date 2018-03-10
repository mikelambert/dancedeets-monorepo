# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import grammar

Any = grammar.Any
Name = grammar.Name

WALTZ = [
    u'keringő',  # hungarian
    u'valcer',  # croatian
    # too popular
    # u'vals',  # romanian
    u'valsa',  # portuguese
    u'valsas',  # lithuanian
    u'valse',  # french
    u'valssi',  # finnish
    u'valzer',  # italian
    u'valčík',  # czech
    u'walc',  # polish
    u'waltz',
    # too popular
    # u'wals',  # dutch
    u'walzer',  # german
    u'βάλς',  # greek
    u'валцер',  # macedonian
    u'вальс',  # russian
    u'медленный вальс',  # slow waltz
    u'английский вальс',  # english waltz
    u'ואלס',  # hebrew
    u'ואלס אנגלי',  # hebrew english waltz
    u'الفالس',  # arabic
    u'เพลงเต้นรำ',  # thai
    u'ワルツ',  # japanese
    u'华尔兹',  # chinese simplified
    u'華爾茲',  # chinese traditional
    u'왈츠',  # korean
]

VIENNESE_WALTZ = [
    u'vals vienés',  # spanish
    u'valsa vienense',  # portuguese
    u'valse viennoise',  # french
    u'valzer viennese',  # italian
    u'viennainen valssi',  # finnish
    u'viennese vals',  # norwegian
    u'viennese valčík',  # czech
    u'viennese waltz',  # english
    u'vienos valsas',  # lithuanian
    u'vietnai keringő',  # hungarian
    u'vijetnamski valcer',  # croatian
    u'viyana vals',  # turkish
    u'vên waltz',  # vietnamese
    u'walca wiedeńskiego',  # polish
    u'weense wals',  # dutch
    u'wiener walzer',  # german
    u'венский вальс',  # russian
    u'виенски валцер',  # macedonian
    u'ואלס וינאי',  # hebrew viennese waltz
    u'الفالس',  # arabic
    u'เพลงวอลทซ์ของชาวเวียนนา',  # thai
    u'ヴィエンヌワルツ',  # japanese
    u'維也納華爾茲',  # chinese traditional
    u'维也纳华尔兹',  # chinese simplified
    u'비엔나왈츠',  # korean
    u'비엔나 ?왈츠',  # korean
]

TANGO = [
    u'tango',
    u'tangó',
    u'ταγκό',  # greek
    u'танго',  # russian, macedonian
    u'та́нго',
    u'טנגו',  # hebrew
    u'تانغو',  # arabic
    u'แทงโก',  # thai
    u'タンゴ',
    u'探戈',
    u'탱고',
]

FOXTROT = [
    u'fokstrot',  # croatian
    u'fokstrotas',  # lithuanian
    # common u'fox',  # spanish
    u'fox-trot',  # french
    u'foxtrot',  # english
    u'foxtrott',  # hungarian
    u'είδος',  # greek
    u'фокстрот',  # macedonian
    u'פוקסטרוט',  # hebrew
    u'خطوةالثعلب',  # arabic
    u'خطوة ?الثعلب',  # arabic
    u'フォックストレイ',  # japanese
    u'狐步舞',  # chinese simplified
    u'폭스트롯',  # korean
    u'폭스 트롯',  # korean
]

QUICKSTEP = [
    u'quickstep',
    u'quick-step',
    u'квикстеп',
    u'การเต้นรำแบบรวดเร็ว',  # thai
    u'クイックステップ',  # japanese
    u'快步',  # chinese simplified
    u'퀵스텝',  # korean
    u'퀵 스텝',  # korean
]

SAMBA = [
    u'samba',  # english
    u'σάμπα',  # greek
    u'самба',  # macedonian
    u'סמבה',  # hebrew
    u'السامبا',  # arabic
    u'แซมบ้า',  # thai
    u'サンバ',  # japanese
    u'桑巴',  # chinese simplified
    u'삼바',  # korean
]

CHACHA = [
    u"צ'הצ'ה",  # hebrew
    u"צ'הצ'הצ'ה",  # hebrew
    u'cha cha',
    u'cha cha cha',
    u'chacha',  # english
    u'chachacha',  # english
    u'ча-ча',  # russian
    u'ча-ча-ча',  # russian
    u'تشاتشا',  # arabic
    u'تشاتشاتشا',  # arabic
    u'チャチャ',  # japanese
    u'チャチャチャ',  # japanese
    u'恰恰',  # chinese simplified
    u'恰恰恰',  # chinese simplified
    u'차차',  # korean
    u'차차차',  # korean
]

RUMBA = [
    u'rumba',  # english
    u'rhumba',  # english
    u'ρούμπα',  # greek
    u'румба',  # macedonian
    u'רומבה',  # hebrew
    u'الرومباةكوبيةزنجية',  # arabic
    u'รำจังหวะรุมบ้า',  # thai
    u'ルンバ',  # japanese
    u'伦巴',  # chinese simplified
    u'倫巴',  # chinese traditional
    u'륨바',  # korean
]

PASO_DOBLE = [
    u'ps. doble',
    u'paso doble',  # thai
    u'пасодобль',  # russian
    u'باسو، دوبل',  # arabic
    u'パゾドブル',  # japanese
    u'파소 도블',  # korean
]

JIVE = [
    u'jive',  # english
    u'джайв',  # russian
    u'ジブ',  # japanese
    u'지브',  # korean
]

EAST_COAST_SWING = [
    u'east coast swing',  # english
    u'ист кост свинг',  # russian
    u'搖擺東海岸',  # japanese
    u'東海岸swing',  # japanese
    u'東海岸のスイング',  # japanese
    u'东海岸swing',  # chinese
    u'東海岸搖擺',  # chinese traditional
    u'이스트코스트스윙',  # korean
    u'이스트 ?코스트 ?스윙',  # korean
]

BOLERO = [
    u'bolero',  # english
    u'boleró',  # hungarian
    u'boléro',  # french
    u'μπολερό',  # greek
    u'болеро',  # russian
    u'בּוֹלֵרוֹ',  # hebrew
    u'رقصة أسبانية',  # arabic
    u'เสื้อชนิดหนึ่ง',  # thai
    u'ボレロ',  # japanese
    u'短上衣',  # chinese simplified
    u'볼레로',  # korean
]

MAMBO = [
    u'mambo',  # english
    u'мамбо',  # macedonian
    u'ממבו',  # hebrew
    u'مامبو',  # arabic
    u'แมมโบ้',  # thai
    u'マンボ',  # japanese
    u'曼波',  # chinese simplified
    u'맘보',  # korean
]

COUNTRY_TWO_STEP = [
    u'country two step'
    u'country 2 step',
    u'country two-step',
    u'country 2-step',
]

AMERICAN_TANGO = [
    u'american tango',  # english
    u'americké tango',  # czech
    u'amerikaanse tango',  # dutch
    u'amerikai tangó',  # hungarian
    u'amerikan tango',  # turkish
    u'amerikanischer tango',  # german
    u'amerikano tango',  # tagalog
    u'amerikansk tango',  # norwegian
    u'amerikietiškas tango',  # lithuanian
    u'amerikkalainen tango',  # finnish
    u'američki tango',  # croatian
    u'amerykańskie tango',  # polish
    u'tango american',  # vietnamese
    u'tango americano',  # portuguese
    u'tango américain',  # french
    u'αμερικανικό ταγκό',  # greek
    u'американски танго',  # macedonian
    u'американское танго',  # russian
    u'טנגו אמריקאי',  # hebrew
    u'تانغو',  # arabic
    u'แทงโก้อเมริกัน',  # thai
    u'アメリカンタンゴ',  # japanese
    u'美国探戈',  # chinese simplified
    u'美國探戈',  # chinese traditional
    u'아메리칸 탱고',  # korean
]

BALLROOM_STYLES = []
BALLROOM_STYLES += WALTZ
BALLROOM_STYLES += VIENNESE_WALTZ
BALLROOM_STYLES += TANGO
BALLROOM_STYLES += QUICKSTEP
BALLROOM_STYLES += SAMBA
BALLROOM_STYLES += CHACHA
BALLROOM_STYLES += RUMBA
BALLROOM_STYLES += PASO_DOBLE
BALLROOM_STYLES += JIVE
BALLROOM_STYLES += EAST_COAST_SWING
BALLROOM_STYLES += BOLERO
BALLROOM_STYLES += MAMBO
BALLROOM_STYLES += COUNTRY_TWO_STEP
BALLROOM_STYLES += AMERICAN_TANGO

LATIN_BALLROOM_STYLES = SAMBA + CHACHA + RUMBA

BALLROOM = Any(
    u'ballroom',
    u'бальные',
    u'ballsaal',  # german
    u'tane\w+ sál',  # czech
    u'salle de bal',  # french
    u'salón de baile',  # spanish
    u'sala balowa',  # polish
    u'бальный',  # russian
    u'phòng khiêu vũ',  # vietnamese
    u'舞廳',
    u'ボールルーム',
    u'사교',
)
