import itertools

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
        return keywords.get_regex_string(keywords.CONNECTOR)

    def as_token_regex(self):
        return keywords.get_regex_string(keywords.CONNECTOR)

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


def connected(a, b):
    return Ordered(a, Connector(), b)

def commutative_connected(a, b):
    return Any(
        connected(a, b),
        connected(b, a),
    )


GOOD_DANCE = 'DANCE'
add(GOOD_DANCE, Any(
    keywords.DANCE,
    commutative_connected(Any(keywords.HOUSE, keywords.FREESTYLE), keywords.EASY_DANCE),
    commutative_connected(keywords.AMBIGUOUS_DANCE_MUSIC, keywords.EASY_DANCE),
    commutative_connected(keywords.STREET, Any(keywords.EASY_CHOREO, keywords.EASY_DANCE)),
))


WRONG_CLASS = 'WRONG_CLASS'
add(WRONG_CLASS, commutative_connected(keywords.AMBIGUOUS_WRONG_STYLE, keywords.CLASS))

WRONG_BATTLE = 'WRONG_BATTLE'
add(WRONG_BATTLE, Any(
    keywords.WRONG_BATTLE,
    commutative_connected(keywords.WRONG_BATTLE_STYLE, Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST))
))

DANCE_STYLE = 'DANCE_STYLE'
add(DANCE_STYLE, Any(keywords.AMBIGUOUS_DANCE_MUSIC, keywords.DANCE, keywords.HOUSE))

# TODO: make sure this doesn't match... 'mc hiphop contest'
GOOD_DANCE_BATTLE = 'GOOD_DANCE_BATTLE'
good_dance = Any(keywords.AMBIGUOUS_DANCE_MUSIC, keywords.DANCE, keywords.HOUSE)
ambiguous_dance = Any(keywords.EASY_DANCE, keywords.EASY_CHOREO)
good_battle = Any(keywords.BATTLE, keywords.N_X_N, keywords.CONTEST)
ambiguous_battle = Any(keywords.EASY_BATTLE)
add(GOOD_DANCE_BATTLE, Any(
    keywords.OBVIOUS_BATTLE,
    connected(keywords.BONNIE_AND_CLYDE, keywords.BATTLE),
    connected(keywords.KING_OF_THE, keywords.CYPHER),
    connected(keywords.CYPHER, keywords.KING),
    commutative_connected(good_dance, good_battle)
))

DANCE_BATTLE = 'DANCE_BATTLE'
add(DANCE_BATTLE, Any(
    get(GOOD_DANCE_BATTLE),
    commutative_connected(good_dance, ambiguous_battle),
    commutative_connected(ambiguous_dance, good_battle),
    commutative_connected(ambiguous_dance, ambiguous_battle),
))

BATTLE = 'BATTLE'
add(BATTLE, Any(keywords.BATTLE, keywords.OBVIOUS_BATTLE))

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
        keywords.DANCE,
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
add(PERFORMANCE_PRACTICE, commutative_connected(keywords.DANCE, Any(keywords.PERFORMANCE, keywords.PRACTICE)))

DANCE_WRONG_STYLE_TITLE = 'DANCE_WRONG_STYLE_TITLE'
add(DANCE_WRONG_STYLE_TITLE, Any(keywords.DANCE_WRONG_STYLE, keywords.DANCE_WRONG_STYLE_TITLE_ONLY))
