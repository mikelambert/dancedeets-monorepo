import codecs
import glob
import itertools
import logging
import re

from . import regex_keywords
from . import re_flatten


def _flatten(listOfLists):
    "Flatten one level of nesting"
    return list(itertools.chain.from_iterable(listOfLists))


class GrammarRule(object):
    """The entire grammar rule tree must be composed of these."""

    def __init__(self):
        self._cached_double_regex = {}

    def hack_double_regex(self, flags=0):
        if flags not in self._cached_double_regex:
            self._cached_double_regex[flags] = regex_keywords.make_regexes_raw(self.as_expanded_regex(), flags=flags)
        return self._cached_double_regex[flags]

    def get_regex_alternations(self):
        return [self.as_expanded_regex()]


class _BaseAlternation(GrammarRule):
    def __init__(self):
        super(_BaseAlternation, self).__init__()
        self._expanded_regex = None
        # Subclass must set up self._keywords

    def children(self):
        return [x for x in self._keywords if not isinstance(x, basestring)]

    @staticmethod
    def flatten_regex(strings):
        try:
            return re_flatten.construct_regex(strings)
        except UnicodeDecodeError as e:
            logging.exception('e %s', e)
            # When we compile a gigantic regex and fail, let's try to compile the component pieces and see where things fall apart
            for line in strings:
                try:
                    line.encode('ascii')
                except UnicodeDecodeError:
                    logging.error("failed to compile: %r: %s", line, line)
                    raise
            logging.fatal("Error constructing regexes")
            raise

    def as_expanded_regex(self):
        if not self._expanded_regex:
            self._expanded_regex = self.flatten_regex(self.get_regex_alternations())
        return self._expanded_regex

    def get_regex_alternations(self):
        assert isinstance(self._keywords, tuple), "keywords are not a tuple: %s" % self._keywords
        alternations = []
        for x in self._keywords:
            if isinstance(x, GrammarRule):
                alternations.extend(x.get_regex_alternations())
            else:
                alternations.append(x)
        return alternations

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._keywords[:20])


class Any(_BaseAlternation):
    def __init__(self, *keywords):
        super(Any, self).__init__()
        non_rule_or_string = [x for x in keywords if not isinstance(x, (GrammarRule, basestring))]
        if non_rule_or_string:
            raise ValueError("Any() arguments need to be str, unicode, or a GrammarRule object: %s" % non_rule_or_string)
        self._keywords = tuple(keywords)


STRONG = 0
STRONG_WEAK = 1


class FileBackedKeyword(_BaseAlternation):
    def __init__(self, filename, strength):
        super(FileBackedKeyword, self).__init__()
        self._filename = filename
        self._strength = strength
        self.__keywords = None

    @property
    def _keywords(self):
        if self.__keywords is None:
            strong_keywords, weak_keywords = self._get_manual_dance_keywords(self._filename)
            if self._strength == STRONG:
                self.__keywords = tuple(strong_keywords)
            elif self._strength == STRONG_WEAK:
                self.__keywords = tuple(strong_keywords + weak_keywords)
            else:
                raise ValueError("Unknown strength %s" % self._strength)
        return self.__keywords

    #TODO(lambert): maybe handle 'byronom coxom' in slovakian with these keywords
    @classmethod
    def _get_manual_dance_keywords(cls, filename):
        import os
        base_dir = os.path.dirname(__file__)
        glob_path = '%s/keywords/%s.txt' % (base_dir, filename)
        lines = []
        for filename in glob.glob(glob_path):
            f = codecs.open(filename, encoding='utf-8')
            lines.extend(f.readlines())
        result = cls._parse_keywords(lines)
        return result

    @classmethod
    def _parse_keywords(cls, lines):
        manual_keywords = []
        dependent_manual_keywords = []
        for line in lines:
            # Strip off comments, unless backquoted escaped
            line = re.sub(r'^((?:[^\\#]|\\.)*)#.*$', '\\1', line).strip()
            if not line:
                continue
            raw_line = re.sub(r'\\[A-Z]', '', line)
            if raw_line != raw_line.lower():
                raise Exception("Keyword contained uppercase characters: %s" % line.encode('utf8'))
            if line.endswith(',0'):
                line = line[:-2]
                dependent_manual_keywords.append(line)
            else:
                manual_keywords.append(line)

        return manual_keywords, dependent_manual_keywords


class Ordered(GrammarRule):
    def __init__(self, *args):
        super(Ordered, self).__init__()
        self.args = args

    def children(self):
        return self.args

    def as_expanded_regex(self):
        return ''.join(x.as_expanded_regex() for x in self.args)

    def __repr__(self):
        return '%s(*%r)' % (self.__class__.__name__, self.args)


class RegexRule(GrammarRule):
    def __init__(self, regex):
        super(RegexRule, self).__init__()
        self.regex = regex

    def children(self):
        return []

    def as_expanded_regex(self):
        return self.regex

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.regex)


class Name(GrammarRule):
    def __init__(self, name, sub_rule):
        super(Name, self).__init__()
        self._name = name
        self._final_name = re.sub(r'[\W_]+', '', self._name)
        self._sub_rule = sub_rule

        # Validate rule integrity
        rules = [sub_rule]
        while rules:
            if not all(isinstance(x, GrammarRule) for x in rules):
                non_rules = [x for x in rules if not isinstance(x, GrammarRule)]
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

    def get_regex_alternations(self):
        return self._sub_rule.get_regex_alternations() + [r'_%s\d*_' % self._final_name]

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self._name, self._sub_rule)
