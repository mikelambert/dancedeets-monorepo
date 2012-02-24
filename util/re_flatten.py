import re
from util import pytrie

def construct_regex(elements):
    trie = pytrie.Trie(dict((tokenize_regex(x), True) for x in elements))
    root = trie._root
    regex = _sub_alternation(root)
    return regex

def _sub_alternation(tree):
    regexes = []
    if tree.value != pytrie.NULL:
        regexes.append('')
    for x in tree.children.keys():
        subtree = tree.children[x]
        regex = _sub_alternation(subtree)
        regexes.append(x + regex)
    if len(regexes) == 1:
        return regexes[0]
    else:
        return u'(?:%s)' % '|'.join(regexes)

QUANTIFIER = '(?:[+*?]|{\d+(?:,\d+)?})?\??'
def tokenize_regex(original_r):
    r = original_r
    tokenized = []
    while r:
          match = re.match(r'\\?[^()\[\]*+?]' + QUANTIFIER, r)
          if match:
              tokenized.append(match.group(0))
            r = r[match.end():]
            continue
        match = re.match(r'^\[(?:[^\]\\]+|\\.)*\]' + QUANTIFIER, r)
        if match:
            tokenized.append(match.group(0))
            r = r[match.end():]
            continue
        match = re.match(r'^\((?:[^\\()]+|\\.)*\)' + QUANTIFIER, r)
        if match:
            tokenized.append(match.group(0))
            r = r[match.end():]
            continue
        if r.startswith('('):
            return original_r
        raise Exception("Cannot parse regex: %r" % r)
    return tuple(tokenized)

if __name__ == '__main__':
    assert ('b', 'o', 'n', 'n', 'i', 'e', '\\s*', '(?:and|&)', '\\s*', 'c', 'l', 'y', 'd', 'e') == tokenize_regex(r"bonnie\s*(?:and|&)\s*clyde")
    assert ('p', 'o', 'p', '\\W{0,3}', 'l', 'o', 'c', 'k', '(?:ing?|er[sz]?)?') == tokenize_regex(r"pop\W{0,3}lock(?:ing?|er[sz]?)?")
    assert ('0', '[ -]?', 'n', 'a', '[ -]?', '0') == tokenize_regex("0[ -]?na[ -]?0"),tokenize_regex("0[ -]?na[ -]?0")
    import logic.event_classifier
    manual_dance_keywords = logic.event_classifier.get_manual_dance_keywords()
    t = pytrie.Trie(dict((tokenize_regex(x), True) for x in manual_dance_keywords))
    regex = _sub_alternation(t._root)
    print regex
