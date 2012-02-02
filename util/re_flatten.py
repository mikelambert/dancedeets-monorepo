from util import pytrie

def construct_regex(elements):
    trie = pytrie.Trie(dict((x, True) for x in elements))
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

if __name__ == '__main__':
    import logic.event_classifier
    manual_dance_keywords = logic.event_classifier.get_manual_dance_keywords()
    t = pytrie.Trie(dict((x, True) for x in manual_dance_keywords))
    regex = sub_alternation(t._root)
    print regex
