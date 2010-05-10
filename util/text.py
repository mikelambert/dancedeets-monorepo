import datetime

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

def date_format(f, d):
    return d.strftime(str(f))

#TODO(lambert): make ampm based on user location
# http://en.wikipedia.org/wiki/12-hour_clock
def date_human_format(d, use_ampm=True):
    now = datetime.datetime.now()
    difference = (d - now)
    month_day_of_week = d.strftime('%A, %B')
    month_day = '%s %s' % (month_day_of_week, d.day)
    if use_ampm:
        time_string = '%d:%02d%s' % (int(d.strftime('%I')), d.minute, d.strftime('%p').lower())
    else:
        time_string = '%d:%02d' % (int(d.strftime('%H')), d.minute)
    return '%s at %s' % (month_day, time_string)


def format(f, s):
    return f % s

