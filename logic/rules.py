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


def connected(a, b):
    return Ordered(a, Connector(), b)

def commutative_connected(a, b):
    return Any(
        connected(a, b),
        connected(b, a),
    )

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
add(GOOD_DANCE_BATTLE, Any(keywords.OBVIOUS_BATTLE, commutative_connected(good_dance, good_battle)))

DANCE_BATTLE = 'DANCE_BATTLE'
add(DANCE_BATTLE, Any(
    get(GOOD_DANCE_BATTLE),
    commutative_connected(good_dance, ambiguous_battle),
    commutative_connected(ambiguous_dance, good_battle),
    commutative_connected(ambiguous_dance, ambiguous_battle),
))

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
add(FULL_JUDGE,Any(
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
# TODO: we need to make a regex of the above rule, but at the start-of-a-line:
# start_judge_keywords_regex = event_classifier.make_regexes(JUDGE_RULE, wrapper='^[^\w\n]*%s', flags=re.MULTILINE)

PERFORMANCE_PRACTICE = 'PERFORMANCE_PRACTICE'
add(PERFORMANCE_PRACTICE, commutative_connected(keywords.DANCE, Any(keywords.PERFORMANCE, keywords.PRACTICE)))
