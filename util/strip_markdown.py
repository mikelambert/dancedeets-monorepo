import re


def strip(s):
    # List Leaders
    s = re.sub(r'^([\s\t]*)(?:[\*\-\+]|\d\.)\s+', '\\1', s, flags=re.MULTILINE)
    # Header
    s = re.sub('\n={2,}', '\n', s)
    # Strikethrough
    s = re.sub(r'~~', '', s)
    # Fenced codeblocks
    s = re.sub(r'`{3}.*\n', '', s)

    # Remove HTML tags
    s = re.sub(r'<(.*?)>', '\1', s)
    # Remove setext-style headers
    s = re.sub(r'^[=\-]{2,}\s*$', '', s)
    # Remove footnotes?
    s = re.sub(r'\[\^.+?\](?:\: .*?$)?', '', s)
    s = re.sub(r'\s{0,2}\[.*?\]: .*?$', '', s)
    # Remove images
    s = re.sub(r'\!\[.*?\][\[\(].*?[\]\)]', '', s)
    # Remove inline links
    s = re.sub(r'\[(.*?)\][\[\(].*?[\]\)]', '\\1', s, flags=re.DOTALL)
    # Remove Blockquotes
    s = re.sub(r'>', '', s)
    # Remove reference-style links?
    s = re.sub(r'^\s{1,2}\[(?:.*?)\]: (?:\S+)(?: ".*?")?\s*$', '', s)
    # Remove atx-style headers
    s = re.sub(r'^\#{1,6}\s*([^#]*)\s*(?:\#{1,6})?', '\\1', s, flags=re.MULTILINE)
    s = re.sub(r'([\*_]{1,3})(\S.*?\S)\1', '\\2', s)
    s = re.sub(r'(`{3,})(.*?)\1', '\\2', s, flags=re.MULTILINE)
    s = re.sub(r'^-{3,}\s*$', '', s)
    s = re.sub(r'`(.+?)`', '\\1', s)
    s = re.sub(r'\n{2,}', '\n\n', s)
    return s
