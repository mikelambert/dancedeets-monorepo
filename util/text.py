# -*-*- encoding: utf-8 -*-*-

import jinja2
import json
import markupsafe
import logging
import re


def format_html(value):
    return jinja2.Markup.escape(value).replace('\n', jinja2.Markup('<br>\n'))


# Commented multi-line version:
url_finder_re = re.compile(r"""
(?xi)
\b
(                            # Capture 1: entire matched URL
    (?:
        https?:                # URL protocol and colon
        (?:
            /{1,3}                        # 1-3 slashes
            |                                #   or
            [a-z0-9%]                        # Single letter or digit or '%'
                                            # (Trying not to match e.g. "URI::Escape")
        )
        |                            #   or
                                    # looks like domain name followed by a slash:
        [a-z0-9.\-]+[.]
        (?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)
        /
    )
    (?:                            # One or more:
        [^\s()<>{}\[\]]+                        # Run of non-space, non-()<>{}[]
        |                                #   or
        \([^\s()]*?\([^\s()]+\)[^\s()]*?\)  # balanced parens, one level deep: (…(…)…)
        |
        \([^\s]+?\)                            # balanced parens, non-recursive: (…)
    )+
    (?:                            # End with:
        \([^\s()]*?\([^\s()]+\)[^\s()]*?\)  # balanced parens, one level deep: (…(…)…)
        |
        \([^\s]+?\)                            # balanced parens, non-recursive: (…)
        |                                    #   or
        [^\s`!()\[\]{};:'".,<>?«»“”‘’]        # not a space or one of these punct chars
    )
    |                    # OR, the following to match naked domains:
    (?:
        (?<!@)            # not preceded by a @, avoid matching foo@_gmail.com_
        [a-z0-9]+
        (?:[.\-][a-z0-9]+)*
        [.]
        (?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)
        \b
        /?
        (?!@)            # not succeeded by a @, avoid matching "foo.na" in "foo.na@example.com"
    )
)
""")


def linkify(value):
    # We don't need to escape the value we send in the href, since everything should be been pre-escaped.
    def make_href(m):
        link = m.group(1)
        if '"' in link:
            logging.error("Found double-quote in link %r in linkify for %r", link, value)
        url = m.group(1)
        if '://' not in url:
            url = 'http://' + url
        return jinja2.Markup('<a href="%s">%s</a>') % (url, m.group(1))
    return url_finder_re.sub(make_href, jinja2.Markup.escape(value))


# This code is taken from django
_base_js_escapes = (
    ('\\', '\\u005C'),
    ('\'', '\\u0027'),
    ('"', '\\u0022'),
    ('>', '\\u003E'),
    ('<', '\\u003C'),
    ('&', '\\u0026'),
    ('=', '\\u003D'),
    ('-', '\\u002D'),
    (';', '\\u003B'),
    ('\u2028', '\\u2028'),
    ('\u2029', '\\u2029')
)

# Escape every ASCII character with a value less than 32.
_js_escapes = (_base_js_escapes +
               tuple([('%c' % z, '\\u%04X' % z) for z in range(32)]))


def escapejs(value):
    """Hex encodes characters for use in JavaScript strings."""
    value = unicode(value)
    for bad, good in _js_escapes:
        value = value.replace(bad, good)
    return markupsafe.Markup(value)


def format_js(value):
    if isinstance(value, basestring):
        value = value.replace('\\', '\\\\')
        value = value.replace('"', '\\"')
        value = value.replace("'", "\\'")
        value = value.replace("\n", "\\n")
        return value
    elif isinstance(value, (int, long, float)):
        return str(value)
    else:
        return ''


def date_format(f, d):
    return d.strftime(str(f)) if d else None


def format(f, s):
    return f % s


# Figure out if simplejson escapes slashes.  This behavior was changed
# from one version to another without reason.
_slash_escape = '\\/' not in json.dumps('/')


def htmlsafe_json_dumps(obj, **kwargs):
    """Works exactly like :func:`dumps` but is safe for use in ``<script>``
    tags.  It accepts the same arguments and returns a JSON string.  Note that
    this is available in templates through the ``|tojson`` filter which will
    also mark the result as safe.  Due to how this function escapes certain
    characters this is safe even if used outside of ``<script>`` tags.
    The following characters are escaped in strings:
    -   ``<``
    -   ``>``
    -   ``&``
    -   ``'``
    This makes it safe to embed such strings in any place in HTML with the
    notable exception of double quoted attributes.  In that case single
    quote your attributes or HTML escape it in addition.
    .. versionchanged:: 0.10
       This function's return value is now always safe for HTML usage, even
       if outside of script tags or if used in XHTML.  This rule does not
       hold true when using this function in HTML attributes that are double
       quoted.  Always single quote attributes if you use the ``|tojson``
       filter.  Alternatively use ``|tojson|forceescape``.
    """
    if obj is None or isinstance(obj, jinja2.Undefined):
        return 'null'
    rv = json.dumps(obj, **kwargs) \
        .replace(u'<', u'\\u003c') \
        .replace(u'>', u'\\u003e') \
        .replace(u'&', u'\\u0026') \
        .replace(u"'", u'\\u0027')
    if not _slash_escape:
        rv = rv.replace('\\/', '/')
    return rv


def tojson_filter(obj, **kwargs):
    return jinja2.Markup(htmlsafe_json_dumps(obj, **kwargs))
