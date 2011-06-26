import datetime
from pytz.gae import pytz

# http://en.wikipedia.org/wiki/12-hour_clock
AMPM_COUNTRIES = ['AU', 'BD', 'CA', 'CO', 'EG', 'IN', 'MY', 'NZ', 'PK', 'PH', 'US']


def localize_timestamp(dt, timezone_str="America/Los_Angeles"):
    # facebook stupidly gives us times localized into a UTC timezone, even though it is timezone-less information. Let's "undo" that here
    timezone = pytz.timezone(timezone_str)
    localized_dt = timezone.localize(dt)
    final_dt = dt + localized_dt.tzinfo.utcoffset(localized_dt)
    return final_dt

def parse_fb_timestamp(fb_timestamp):
    # because of events like 23705144628 without any time information
    if not fb_timestamp:
        return datetime.datetime(1970, 1, 1)

    # If we access events with an access_token (necessary to get around DOS limits from overloaded appengine IPs), we get a timestamp-localized weirdly-timed time from facebook, and need to reverse-engineer it
    if '+' in fb_timestamp:
        return localize_timestamp(datetime.datetime.strptime(fb_timestamp.split('+')[0], '%Y-%m-%dT%H:%M:%S'))
    else:
        return datetime.datetime.strptime(fb_timestamp, '%Y-%m-%dT%H:%M:%S')

def time_human_format(d, country):
    if not country or country in AMPM_COUNTRIES:
        time_string = '%d:%02d%s' % (int(d.strftime('%I')), d.minute, d.strftime('%p').lower())
    else:
        time_string = '%d:%02d' % (int(d.strftime('%H')), d.minute)
    return time_string

def date_human_format(d, country=None):
    month_day_of_week = d.strftime('%A, %B')
    month_day = '%s %s' % (month_day_of_week, d.day)
    time_string = time_human_format(d, country=country)
    return '%s - %s' % (month_day, time_string)

def duration_human_format(d1, d2, country=None):
    first_date = date_human_format(d1)
    if (d2 - d1) > datetime.timedelta(hours=24):
        second_date = date_human_format(d2, country)
    else:
        second_date = time_human_format(d2, country)
    return "%s to %s" % (first_date, second_date)

