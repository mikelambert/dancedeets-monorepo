import itertools
import re

import keywords
import regex_keywords

_rules = {}
def add(name, rule):
    rules = [rule]
    # Validate rule integrity
    while rules:
        if not all(isinstance(x, keywords.GrammarRule) for x in rules):
            non_rules = [x for x in rules if not isinstance(x, keywords.GrammarRule)]
            raise ValueError("Found non-GrammarRule in input rule %s: %s" % (rule, non_rules))
        rules = list(itertools.chain(*(list(x.children()) for x in rules)))
    _rules[name] = rule


def get(name):
    return _rules[name]

class Any(keywords.GrammarRule):
    def __init__(self, *args):
        self.args = args

    def children(self):
        return self.args

    def as_expanded_regex(self):
        return regex_keywords.make_regex_string(x.as_expanded_regex() for x in self.args)

    def as_token_regex(self):
        return regex_keywords.make_regex_string(x.as_token_regex() for x in self.args)

    def __repr__(self):
        return 'Any(*%r)' % (self.args,)

class Ordered(keywords.GrammarRule):
    def __init__(self, *args):
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
        self._name = name
        self._final_name = re.sub(r'[\W_]+', '', self._name)
        self._sub_rule = sub_rule

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


DANCE = 'DANCE'
add(DANCE, NamedRule('DANCE', Any(
    keywords.DANCE,
    keywords.STYLE_BREAK,
    keywords.STYLE_ROCK,
    keywords.STYLE_POP,
    keywords.STYLE_LOCK,
    keywords.STYLE_WAACK,
    keywords.STYLE_ALLSTYLE,
)))

GOOD_DANCE = 'GOOD_DANCE'
add(GOOD_DANCE, NamedRule('GOOD_DANCE', Any(
    get(DANCE),
    keywords.VOGUE,
    commutative_connected(Any(keywords.HOUSE, keywords.FREESTYLE), keywords.EASY_DANCE),
    commutative_connected(keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_DANCE),
    commutative_connected(keywords.STREET, Any(keywords.EASY_CHOREO, keywords.EASY_DANCE)),
    # This may seem strange to list it essentially twice ,but necessary for "battles de danses breakdance"
    commutative_connected(keywords.EASY_DANCE, get(DANCE)),
)))

DECENT_DANCE = 'DECENT_DANCE'
add(DECENT_DANCE, Any(
    get(GOOD_DANCE),
    keywords.AMBIGUOUS_DANCE_MUSIC,
))

WRONG_CLASS = 'WRONG_CLASS'
add(WRONG_CLASS, commutative_connected(keywords.AMBIGUOUS_WRONG_STYLE, keywords.CLASS))

WRONG_BATTLE = 'WRONG_BATTLE'
add(WRONG_BATTLE, Any(
    keywords.WRONG_BATTLE,
    commutative_connected(keywords.WRONG_BATTLE_STYLE, Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST))
))

DANCE_STYLE = 'DANCE_STYLE'
add(DANCE_STYLE, Any(keywords.AMBIGUOUS_DANCE_MUSIC, get(DANCE), keywords.VOGUE, keywords.HOUSE))

# TODO: make sure this doesn't match... 'mc hiphop contest'
GOOD_DANCE_BATTLE = 'GOOD_DANCE_BATTLE'
# 'hip hop battle' by itself isnt sufficient, so leave that in ambiguous_battle_dance.
# GOOD_DANCE does include 'hip hop dance' though, to allow 'hip hop dance battle' to work.
good_battle_dance = Any(get(GOOD_DANCE), keywords.HOUSE)
ambiguous_battle_dance = Any(keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_DANCE, keywords.EASY_CHOREO)
good_battle = Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST)
ambiguous_battle = Any(keywords.EASY_BATTLE)
add(GOOD_DANCE_BATTLE, Any(
    keywords.OBVIOUS_BATTLE,
    connected(keywords.BONNIE_AND_CLYDE, keywords.BATTLE),
    connected(keywords.KING_OF_THE, keywords.CYPHER),
    connected(keywords.CYPHER, keywords.KING),
    commutative_connected(good_battle_dance, good_battle)
))

DANCE_BATTLE = 'DANCE_BATTLE'
add(DANCE_BATTLE, Any(
    get(GOOD_DANCE_BATTLE),
    commutative_connected(good_battle_dance, ambiguous_battle),
    commutative_connected(ambiguous_battle_dance, good_battle),
    commutative_connected(ambiguous_battle_dance, ambiguous_battle),
))

BATTLE = 'BATTLE'
add(BATTLE, Any(keywords.BATTLE, keywords.OBVIOUS_BATTLE))

good_dance = Any(keywords.AMBIGUOUS_DANCE_MUSIC, get(GOOD_DANCE), keywords.HOUSE)

GOOD_DANCE_CLASS = 'GOOD_DANCE_CLASS'
add(GOOD_DANCE_CLASS, Any(
    commutative_connected(good_dance, keywords.CLASS),
    # only do one direction here, since we don't want "house stage" and "funk stage"
    connected(keywords.AMBIGUOUS_CLASS, good_dance),
))
# TODO: is this one necessary? we could do it as a regex, but we could also do it as a rule...
EXTENDED_CLASS = 'EXTENDED_CLASS'
add(EXTENDED_CLASS, Any(keywords.CLASS, keywords.AMBIGUOUS_CLASS))

FULL_JUDGE = 'FULL_JUDGE'
add(FULL_JUDGE, Any(
    keywords.JUDGE,
    commutative_connected(keywords.JUDGE, Any(
        get(GOOD_DANCE),
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

PERFORMANCE_PRACTICE = 'PERFORMANCE_PRACTICE'
add(PERFORMANCE_PRACTICE, commutative_connected(get(GOOD_DANCE), Any(keywords.PERFORMANCE, keywords.PRACTICE)))

DANCE_WRONG_STYLE_TITLE = 'DANCE_WRONG_STYLE_TITLE'
add(DANCE_WRONG_STYLE_TITLE, Any(keywords.DANCE_WRONG_STYLE, keywords.DANCE_WRONG_STYLE_TITLE_ONLY))

event_keywords = [
    keywords.CLASS,
    keywords.N_X_N,
    keywords.BATTLE,
    keywords.OBVIOUS_BATTLE,
    keywords.AUDITION,
    keywords.CYPHER,
    keywords.JUDGE,
]

EVENT = 'EVENT'
add(EVENT, Any(*event_keywords))

EVENT_WITH_ROMANCE_EVENT = 'EVENT_WITH_ROMANCE_EVENT'
add(EVENT_WITH_ROMANCE_EVENT, Any(keywords.AMBIGUOUS_CLASS, *event_keywords))
