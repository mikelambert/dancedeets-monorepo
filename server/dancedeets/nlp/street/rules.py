from .. import grammar
from . import keywords
Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

MUSIC = Name('MUSIC', Any(
    keywords.AMBIGUOUS_DANCE_MUSIC,
    keywords.MUSIC_ONLY,
))

STREET_STYLES = Any(
    keywords.STYLE_BREAK,
    keywords.STYLE_ROCK,
    keywords.STYLE_POP,
    keywords.STYLE_LOCK,
    keywords.STYLE_WAACK,
    keywords.STYLE_HOUSE,
    keywords.STYLE_HIPHOP,
    keywords.STYLE_DANCEHALL,
    keywords.STYLE_KRUMP,
    keywords.STYLE_TURF,
    keywords.STYLE_LITEFEET,
    keywords.STYLE_FLEX,
    keywords.STYLE_BEBOP,
    keywords.STYLE_ALLSTYLE,
)

DANCE = Name('DANCE', Any(
    keywords.DANCE,
    STREET_STYLES,
))

GOOD_DANCE = Name(
    'GOOD_DANCE',
    Any(
        DANCE,
        keywords.VOGUE,
        # This may seem strange to list 'dance dance' essentially twice,
        # but necessary for "battles de danses breakdance" or 'afro-house dance workshop'.
        commutative_connected(Any(keywords.HOUSE, keywords.FREESTYLE, keywords.AMBIGUOUS_DANCE_MUSIC, DANCE), keywords.EASY_DANCE),
        commutative_connected(keywords.STREET, Any(keywords.EASY_CHOREO, keywords.EASY_DANCE)),
    )
)

DECENT_DANCE = Name('DECENT_DANCE', Any(
    GOOD_DANCE,
    keywords.AMBIGUOUS_DANCE_MUSIC,
))

WRONG_CLASS = Name('WRONG_CLASS', commutative_connected(keywords.AMBIGUOUS_WRONG_STYLE, keywords.CLASS))

WRONG_BATTLE = Name(
    'WRONG_BATTLE',
    Any(keywords.WRONG_BATTLE, commutative_connected(keywords.WRONG_BATTLE_STYLE, Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST)))
)

RIGHT_NAME_WRONG_KIND = Name(
    'RIGHT_NAME_WRONG_KIND', Any(
        keywords.WRONG_HOUSE,
        keywords.WRONG_BREAK,
        keywords.WRONG_LOCK,
        keywords.WRONG_FLEX,
    )
)

DANCE_STYLE = Name('DANCE_STYLE', Any(keywords.AMBIGUOUS_DANCE_MUSIC, DANCE, keywords.VOGUE, keywords.HOUSE))

# TODO: make sure this doesn't match... 'mc hiphop contest'
# 'hip hop battle' by itself isnt sufficient, so leave that in ambiguous_battle_dance.
# GOOD_DANCE does include 'hip hop dance' though, to allow 'hip hop dance battle' to work.
# In the meantime, we miss https://www.facebook.com/events/788310961258392/ and '2v2 breakin battle'
good_battle_dance = Any(GOOD_DANCE, keywords.HOUSE)
ambiguous_battle_dance = Any(keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_DANCE, keywords.EASY_CHOREO)
good_battle = Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST)
ambiguous_battle = Any(keywords.JAM)
GOOD_DANCE_BATTLE = Name(
    'GOOD_DANCE_BATTLE',
    Any(
        keywords.OBVIOUS_BATTLE, connected(keywords.BONNIE_AND_CLYDE, keywords.BATTLE),
        grammar.Ordered(Any('king of (?:the )?'), keywords.CYPHER), connected(keywords.CYPHER, Any('king')),
        commutative_connected(good_battle_dance, good_battle)
    )
)

DANCE_BATTLE = Name(
    'DANCE_BATTLE',
    Any(
        GOOD_DANCE_BATTLE,
        commutative_connected(good_battle_dance, ambiguous_battle),
        commutative_connected(ambiguous_battle_dance, good_battle),
        commutative_connected(ambiguous_battle_dance, ambiguous_battle),
    )
)

BATTLE = Name('BATTLE', Any(keywords.BATTLE, keywords.OBVIOUS_BATTLE))

good_dance = Any(keywords.AMBIGUOUS_DANCE_MUSIC, GOOD_DANCE, keywords.HOUSE)

GOOD_DANCE_CLASS = Name(
    'GOOD_DANCE_CLASS',
    Any(
        commutative_connected(good_dance, keywords.CLASS),
        # only do one direction here, since we don't want "house stage" and "funk stage"
        connected(keywords.ROMANCE_LANGUAGE_CLASS, good_dance),
    )
)
# TODO: is this one necessary? we could do it as a regex, but we could also do it as a rule...
ROMANCE_EXTENDED_CLASS = Name('ROMANCE_EXTENDED_CLASS', Any(keywords.CLASS, keywords.ROMANCE_LANGUAGE_CLASS))
ROMANCE_EXTENDED_CLASS_ONLY = Name('ROMANCE_EXTENDED_CLASS_ONLY', Any(keywords.CLASS_ONLY, keywords.ROMANCE_LANGUAGE_CLASS))

full_judge = Any(
    keywords.JUDGE,
    commutative_connected(
        keywords.JUDGE,
        Any(
            GOOD_DANCE, keywords.EASY_DANCE, keywords.AMBIGUOUS_DANCE_MUSIC, keywords.HOUSE, keywords.EASY_CHOREO, keywords.CONTEST,
            keywords.BATTLE, keywords.N_X_N
        )
    )
)

start_line = grammar.RegexRule(r'^(?m)[^\w\n]*')

START_JUDGE = Name('START_JUDGE', grammar.Ordered(start_line, full_judge))

PERFORMANCE_PRACTICE = Name('PERFORMANCE_PRACTICE', commutative_connected(GOOD_DANCE, Any(keywords.PERFORMANCE, keywords.PRACTICE)))

DANCE_WRONG_STYLE_TITLE = Name('DANCE_WRONG_STYLE_TITLE', Any(keywords.DANCE_WRONG_STYLE, keywords.DANCE_WRONG_STYLE_TITLE_ONLY))

EVENT = Name(
    'EVENT',
    Any(
        keywords.CLASS,
        keywords.N_X_N,
        keywords.BATTLE,
        keywords.OBVIOUS_BATTLE,
        keywords.AUDITION,
        keywords.CYPHER,
        keywords.JUDGE,
    )
)

EVENT_WITH_ROMANCE_EVENT = Name('EVENT_WITH_ROMANCE_EVENT', Any(keywords.ROMANCE_LANGUAGE_CLASS, EVENT))

MANUAL_DANCER = [
    Name(
        'MANUAL_DANCER',
        Any(
            keywords.BBOY_CREW[i],
            keywords.BBOY_DANCER[i],
            keywords.CHOREO_CREW[i],
            keywords.CHOREO_DANCER[i],
            keywords.FREESTYLE_CREW[i],
            keywords.FREESTYLE_DANCER[i],
        )
    ) for i in [grammar.STRONG, grammar.STRONG_WEAK]
]

MANUAL_DANCE = [
    Name(
        'MANUAL_DANCE',
        Any(
            MANUAL_DANCER[i],
            keywords.CHOREO_KEYWORD[i],
            keywords.FREESTYLE_KEYWORD[i],
            keywords.COMPETITION[i],
            keywords.GOOD_DJ[i],
        )
    ) for i in [grammar.STRONG, grammar.STRONG_WEAK]
]

GOOD_SOLO_LINE = Name('GOOD_SOLO_LINE', Any(GOOD_DANCE, MANUAL_DANCER[grammar.STRONG]))

ANY_BAD = Name('ANY_BAD', Any(
    keywords.CLUB_ONLY,
    keywords.DANCE_WRONG_STYLE,
))

STREET_STYLE = Name(
    'STREET_STYLE',
    Any(
        DANCE,
        keywords.AMBIGUOUS_DANCE_MUSIC,
        keywords.HOUSE,
        keywords.FREESTYLE,
        keywords.STREET,
        keywords.VOGUE,
        keywords.EASY_VOGUE,
        keywords.TOO_EASY_VOGUE,
    )
)

ANY_GOOD = Name(
    'ANY_GOOD',
    Any(
        MANUAL_DANCE[grammar.STRONG],  # includes MANUAL_DANCER
        keywords.EASY_DANCE,
        keywords.EASY_CHOREO,
        STREET_STYLE,
        keywords.TOO_EASY_VOGUE,
        keywords.BONNIE_AND_CLYDE,
        EVENT,
        keywords.EVENT,
        keywords.EASY_EVENT,
        keywords.JAM,
        keywords.JUDGE,
        keywords.PRACTICE,
        keywords.PERFORMANCE,
        keywords.CONTEST,
        keywords.FORMAT_TYPE,
        keywords.ROMANCE_LANGUAGE_CLASS,
    )
)
