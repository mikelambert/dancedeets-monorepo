# -*-*- encoding: utf-8 -*-*-

import logging
import re
from spitfire.runtime import udn
from spitfire.runtime.filters import skip_filter

@skip_filter
def format_html(value):
    return html_escape(value).replace('\n', '<br>\n')

 
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


@skip_filter
def linkify(value):
    # We don't need to escape the value we send in the href, since everything should be been pre-escaped.
    def make_href(m):
        link = m.group(1)
        if '"' in link:
            logging.error("Found double-quote in link %r in linkify for %r", link, value)
        url = m.group(1)
        if not url.startswith('http'):
            url = 'http://' + url
        return '<a href="%s">%s</a>' % (url, m.group(1))
    return url_finder_re.sub(make_href, value)

@skip_filter
def format_js(value):
    if isinstance(value, basestring):
        value = value.replace('\\', '\\\\')
        value = value.replace('"', '\\"')
        value = value.replace("'", "\\'")
        value = value.replace("\n", "\\n")
        return value
    elif isinstance(value, udn.UndefinedPlaceholder):
        # trigger asplosion!
        return str(value.name)
    elif isinstance(value, (int, long, float)):
        return str(value)
    else:
        return ''
    
def html_escape(value):
    if isinstance(value, basestring):
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        value = value.replace('"', '&quot;')
        return value
    elif isinstance(value, udn.UndefinedPlaceholder):
        # trigger asplosion!
        return str(value.name)
    elif isinstance(value, (int, long, float)):
        return str(value)
    else:
        return ''

def date_format(f, d):
    return d.strftime(str(f)) if d else None

def format(f, s):
    return f % s

