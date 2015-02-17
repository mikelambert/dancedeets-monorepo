import itertools
import re

import keywords
from util import re_flatten

class Any(keywords.GrammarRule):
    def __init__(self, *args):
        super(Any, self).__init__()
        self.args = args

    def children(self):
        return self.args

    def as_expanded_regex(self):
        return re_flatten.construct_regex(x.as_expanded_regex() for x in self.args)

    def as_token_regex(self):
        return re_flatten.construct_regex(x.as_token_regex() for x in self.args)

    def __repr__(self):
        return 'Any(*%r)' % (self.args,)

class Ordered(keywords.GrammarRule):
    def __init__(self, *args):
        super(Ordered, self).__init__()
        self.args = args

    def children(self):
        return self.args

    def as_expanded_regex(self):
        return ''.join(x.as_expanded_regex() for x in self.args)

    def as_token_regex(self):
        return ''.join(x.as_token_regex() for x in self.args)

    def __repr__(self):
        return 'Ordered(*%r)' % (self.args,)

class Connector(keywords.GrammarRule):

    def children(self):
        return []

    def as_expanded_regex(self):
        return keywords.CONNECTOR.as_expanded_regex()

    def as_token_regex(self):
        return keywords.CONNECTOR.as_expanded_regex()

    def __repr__(self):
        return 'Connector()'

class RegexRule(keywords.GrammarRule):
    def __init__(self, regex):
        super(RegexRule, self).__init__()
        self.regex = regex

    def children(self):
        return []

    def as_expanded_regex(self):
        return self.regex

    def as_token_regex(self):
        return self.regex

    def __repr__(self):
        return 'RegexRule(%r)' % self.regex

class NamedRule(keywords.GrammarRule):
    def __init__(self, name, sub_rule):
        super(NamedRule, self).__init__()
        self._name = name
        self._final_name = re.sub(r'[\W_]+', '', self._name)
        self._sub_rule = sub_rule

        # Validate rule integrity
        rules = [sub_rule]
        while rules:
            if not all(isinstance(x, keywords.GrammarRule) for x in rules):
                non_rules = [x for x in rules if not isinstance(x, keywords.GrammarRule)]
                raise ValueError("Found non-GrammarRule in input rule %s: %s" % (sub_rule, non_rules))
            rules = list(itertools.chain(*(list(x.children()) for x in rules)))

    def replace_string(self, *args):
        if args:
            extra_hash = abs(hash(args[0]))
        else:
            extra_hash = ''
        return '_%s%s_' % (self._final_name, extra_hash)

    def children(self):
        return [self._sub_rule]

    def as_expanded_regex(self):
        return self._sub_rule.as_expanded_regex()

    def as_token_regex(self):
        return self._sub_rule.as_token_regex()

    def __repr__(self):
        return 'NamedRule(%s, %r)' % (self._name, self._sub_rule)

def connected(a, b):
    return Ordered(a, Connector(), b)

def commutative_connected(a, b):
    return Any(
        connected(a, b),
        connected(b, a),
    )


DANCE = NamedRule('DANCE', Any(
    keywords.DANCE,
    keywords.STYLE_BREAK,
    keywords.STYLE_ROCK,
    keywords.STYLE_POP,
    keywords.STYLE_LOCK,
    keywords.STYLE_WAACK,
    keywords.STYLE_ALLSTYLE,
))

GOOD_DANCE = NamedRule('GOOD_DANCE', Any(
    DANCE,
    keywords.VOGUE,
    commutative_connected(Any(keywords.HOUSE, keywords.FREESTYLE), keywords.EASY_DANCE),
    commutative_connected(keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_DANCE),
    commutative_connected(keywords.STREET, Any(keywords.EASY_CHOREO, keywords.EASY_DANCE)),
    # This may seem strange to list it essentially twice ,but necessary for "battles de danses breakdance"
    commutative_connected(keywords.EASY_DANCE, DANCE),
))

DECENT_DANCE = NamedRule('DECENT_DANCE', Any(
    GOOD_DANCE,
    keywords.AMBIGUOUS_DANCE_MUSIC,
))

WRONG_CLASS = NamedRule('WRONG_CLASS',
    commutative_connected(keywords.AMBIGUOUS_WRONG_STYLE, keywords.CLASS))

WRONG_BATTLE = NamedRule('WRONG_BATTLE', Any(
    keywords.WRONG_BATTLE,
    commutative_connected(keywords.WRONG_BATTLE_STYLE, Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST))
))

DANCE_STYLE = NamedRule('DANCE_STYLE',
    Any(keywords.AMBIGUOUS_DANCE_MUSIC, DANCE, keywords.VOGUE, keywords.HOUSE))

# TODO: make sure this doesn't match... 'mc hiphop contest'
# 'hip hop battle' by itself isnt sufficient, so leave that in ambiguous_battle_dance.
# GOOD_DANCE does include 'hip hop dance' though, to allow 'hip hop dance battle' to work.
good_battle_dance = Any(GOOD_DANCE, keywords.HOUSE)
ambiguous_battle_dance = Any(keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_DANCE, keywords.EASY_CHOREO)
good_battle = Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST)
ambiguous_battle = Any(keywords.EASY_BATTLE)
GOOD_DANCE_BATTLE = NamedRule('GOOD_DANCE_BATTLE', Any(
    keywords.OBVIOUS_BATTLE,
    connected(keywords.BONNIE_AND_CLYDE, keywords.BATTLE),
    connected(keywords.KING_OF_THE, keywords.CYPHER),
    connected(keywords.CYPHER, keywords.KING),
    commutative_connected(good_battle_dance, good_battle)
))

DANCE_BATTLE = NamedRule('DANCE_BATTLE', Any(
    GOOD_DANCE_BATTLE,
    commutative_connected(good_battle_dance, ambiguous_battle),
    commutative_connected(ambiguous_battle_dance, good_battle),
    commutative_connected(ambiguous_battle_dance, ambiguous_battle),
))

BATTLE = NamedRule('BATTLE',
    Any(keywords.BATTLE, keywords.OBVIOUS_BATTLE))

good_dance = Any(keywords.AMBIGUOUS_DANCE_MUSIC, GOOD_DANCE, keywords.HOUSE)

GOOD_DANCE_CLASS = NamedRule('GOOD_DANCE_CLASS', Any(
    commutative_connected(good_dance, keywords.CLASS),
    # only do one direction here, since we don't want "house stage" and "funk stage"
    connected(keywords.AMBIGUOUS_CLASS, good_dance),
))
# TODO: is this one necessary? we could do it as a regex, but we could also do it as a rule...
EXTENDED_CLASS = NamedRule('EXTENDED_CLASS',
    Any(keywords.CLASS, keywords.AMBIGUOUS_CLASS))

FULL_JUDGE = NamedRule('FULL_JUDGE', Any(
    keywords.JUDGE,
    commutative_connected(keywords.JUDGE, Any(
        GOOD_DANCE,
        keywords.EASY_DANCE,
        keywords.AMBIGUOUS_DANCE_MUSIC,
        keywords.HOUSE,
        keywords.EASY_CHOREO,
        keywords.CONTEST,
        keywords.BATTLE,
        keywords.N_X_N
    )
)))
# TODO(lambert): Maybe add a special RegexRule that I can fill with '^[^\w\n]*', and encapsulate that here instead of client code

PERFORMANCE_PRACTICE = NamedRule('PERFORMANCE_PRACTICE',
    commutative_connected(GOOD_DANCE, Any(keywords.PERFORMANCE, keywords.PRACTICE)))

DANCE_WRONG_STYLE_TITLE = NamedRule('DANCE_WRONG_STYLE_TITLE',
    Any(keywords.DANCE_WRONG_STYLE, keywords.DANCE_WRONG_STYLE_TITLE_ONLY))

event_keywords = [
    keywords.CLASS,
    keywords.N_X_N,
    keywords.BATTLE,
    keywords.OBVIOUS_BATTLE,
    keywords.AUDITION,
    keywords.CYPHER,
    keywords.JUDGE,
]

EVENT = NamedRule('EVENT',
    Any(*event_keywords))

EVENT_WITH_ROMANCE_EVENT = NamedRule('EVENT_WITH_ROMANCE_EVENT',
    Any(keywords.AMBIGUOUS_CLASS, *event_keywords))


MANUAL_DANCER = [NamedRule('MANUAL_DANCER', Any(
    keywords.BBOY_CREW[i],
    keywords.BBOY_DANCER[i],
    keywords.CHOREO_CREW[i],
    keywords.CHOREO_DANCER[i],
    keywords.FREESTYLE_CREW[i],
    keywords.FREESTYLE_DANCER[i],
    )) for i in [keywords.STRONG, keywords.STRONG_WEAK]]

MANUAL_DANCE = [NamedRule('MANUAL_DANCE', Any(
    MANUAL_DANCER[i],
    keywords.CHOREO_KEYWORD[i],
    keywords.FREESTYLE_KEYWORD[i],
    keywords.COMPETITION[i],
    keywords.GOOD_DJ[i],
    )) for i in [keywords.STRONG, keywords.STRONG_WEAK]]


ANY_BAD = NamedRule('ANY_BAD', Any(
    keywords.CLUB_ONLY,
    keywords.DANCE_WRONG_STYLE,
    ))

ANY_GOOD = NamedRule('ANY_GOOD', Any(
    keywords.EASY_DANCE,
    keywords.EASY_EVENT,
    keywords.EASY_BATTLE,
    keywords.STYLE_BREAK,
    keywords.STYLE_ROCK,
    keywords.STYLE_POP,
    keywords.STYLE_LOCK,
    keywords.STYLE_WAACK,
    keywords.STYLE_ALLSTYLE,
    keywords.DANCE,
    keywords.PRACTICE,
    keywords.PERFORMANCE,
    keywords.CONTEST,
    keywords.AMBIGUOUS_DANCE_MUSIC,
    keywords.EASY_CHOREO,
    keywords.CLASS,
    keywords.N_X_N,
    keywords.BATTLE,
    keywords.OBVIOUS_BATTLE,
    keywords.AUDITION,
    keywords.CYPHER,
    keywords.JUDGE,
    keywords.HOUSE,
    keywords.FREESTYLE,
    keywords.STREET,
    keywords.EVENT,
    keywords.AMBIGUOUS_CLASS,
    keywords.FORMAT_TYPE,
    keywords.VOGUE,
    keywords.EASY_VOGUE,
    keywords.BONNIE_AND_CLYDE,
    MANUAL_DANCE[keywords.STRONG], # includes MANUAL_DANCER
))
