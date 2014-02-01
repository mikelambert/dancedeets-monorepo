from spitfire.runtime import udn
from spitfire.runtime.filters import skip_filter

@skip_filter
def format_html(value):
    return html_escape(value).replace('\n', '<br>\n')

@skip_filter
def format_js(value):
    if isinstance(value, basestring):
        value = value.replace('"', '\"')
        value = value.replace("'", "\'")
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
    return d.strftime(str(f))

def format(f, s):
    return f % s

