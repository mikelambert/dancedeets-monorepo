import itertools
from . import cjk_detect
from . import regex_keywords


def _flatten(listOfLists):
    "Flatten one level of nesting"
    return list(itertools.chain.from_iterable(listOfLists))


class StringProcessor(object):
    def __init__(self, text, match_on_word_boundaries=None, lowercase=True):
        text = text.replace('#', '')
        self.text = text.lower() if lowercase else text

        if match_on_word_boundaries is not None:
            self.match_on_word_boundaries = match_on_word_boundaries
        else:
            if cjk_detect.cjk_regex.search(text):
                self.match_on_word_boundaries = regex_keywords.NO_WORD_BOUNDARIES
            else:
                self.match_on_word_boundaries = regex_keywords.WORD_BOUNDARIES
        self._get_token_cache = {}
        self._has_token_cache = {}

    def __repr__(self):
        return 'StringProcessor(%r)' % self.text

    def tokenize(self, token):
        """Tokenizes the relevant bits of this String. Replaces all instances of the token's regex, with the token's string representation.
        """
        # Don't actually tokenize most things, turns out there's no runtime performance advantage, and a quality hit.
        return
        # I tried a bunch of implementations for speed here. This approach appears to be the fastest:
        # Run tokenize for each regex, doing a brute force search-and-replace on the string. (+70sec)
        # We used to include a lambda-replace function to grab the contents, but later realized the original matched string is irrelevant to our use cases.
        #
        # Other ideas that didn't work included:
        # - Do this as a matching-regex with one match group per token, to figure out which token matched. (+waaaay to slow)
        # - In a non-matching regex, but with the matched text, run a matching-regex to figure out which token matched. (+150sec)
        # - In a non-matching regex, but with the matched text, run each token regex by hand to see which matched. (+100sec)
        # - Do one pass for findall to get tokens, and another for sub to replace with the magic token. (+100sec)
        # Could have explored O(lgN) search options for a couple of the above, but it felt like the overhead of entering/exiting re2 was the biggest cost.

    def replace_with(self, token, replace_func, flags=0):
        self.text, count = token.hack_double_regex(flags=flags)[self.match_on_word_boundaries].subn(replace_func, self.text)
        return self.text, count

    def real_tokenize(self, token):
        def word_with_hash(match):
            return token.replace_string(match.group(0))

        _, count = self.replace_with(token, word_with_hash)
        # If we want to get the matched results/keywords too, then we should only do that conditinoally on count, here:
        #if count:
        #    self._get_token_cache[token].extend(token.hack_double_regex()[self.match_on_word_boundaries].findall(self.text))

    def has_token(self, token):
        if token not in self._has_token_cache:
            if token in self._get_token_cache:
                if self._get_token_cache[token]:
                    self._has_token_cache[token] = self._get_token_cache[token][0]
                else:
                    self._has_token_cache[token] = None
            else:
                match = token.hack_double_regex()[self.match_on_word_boundaries].search(self.text)
                if match:
                    self._has_token_cache[token] = match.group(0)
                else:
                    self._has_token_cache[token] = None
        return self._has_token_cache[token]

    def count_tokens(self, token):
        _, count = token.hack_double_regex()[self.match_on_word_boundaries].subn('', self.text)
        return count

    def _get_token(self, token):
        if token not in self._get_token_cache:
            self._get_token_cache[token] = token.hack_double_regex()[self.match_on_word_boundaries].findall(self.text)
        return self._get_token_cache[token]

    def get_tokens(self, *tokens):
        # This is an optimization that saves us 1+ second per 10K runs
        if len(tokens) == 1:
            return self._get_token(tokens[0])
        else:
            return _flatten([self._get_token(token) for token in tokens])

    def get_tokenized_text(self):
        return self.text

    def delete_with_rule(self, rule):
        regexes = rule.hack_double_regex()
        trimmed_text = regexes[self.match_on_word_boundaries].sub('', self.text)
        return StringProcessor(trimmed_text, self.match_on_word_boundaries, lowercase=False)
