from spitfire.runtime import udn
from spitfire.runtime.filters import skip_filter

def spit_filtered(func):
    return skip_filter(func)


@spit_filtered
def format_html(value):
    return html_escape(value).replace('\n', '<br>\n')

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

