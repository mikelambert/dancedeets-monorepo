import datetime

# http://en.wikipedia.org/wiki/12-hour_clock
AMPM_COUNTRIES = ['AU', 'BD', 'CA', 'CO', 'EG', 'IN', 'MY', 'NZ', 'PK', 'PH', 'US']

def parse_fb_timestamp(fb_timestamp):
    # because of events like 23705144628 without any time information
    if not fb_timestamp:
        return None
    try:
        return datetime.datetime.strptime(fb_timestamp, '%Y-%m-%d') # .date()
    except ValueError:
        # intentionally ignore timezone, since we care about representing the time zone in the event's local point of view
        return datetime.datetime.strptime(fb_timestamp[:19], '%Y-%m-%dT%H:%M:%S')

def parse_fb_start_time(fb_event):
    return parse_fb_timestamp(fb_event['info'].get('start_time'))

def parse_fb_end_time(fb_event, need_result=False):
    result = parse_fb_timestamp(fb_event['info'].get('end_time'))
    if need_result:
        result = faked_end_time(parse_fb_start_time(fb_event), result)
    return result

def faked_end_time(start_time, end_time):
    if end_time:
        return end_time
    else:
        if start_time.hour or start_time.minute:
            return start_time + datetime.timedelta(hours=24)
        else:
            return start_time + datetime.timedelta(hours=4*24)

def time_human_format(d, country=None):
    if not country or country in AMPM_COUNTRIES:
        time_string = '%d:%02d%s' % (int(d.strftime('%I')), d.minute, d.strftime('%p').lower())
    else:
        time_string = '%d:%02d' % (int(d.strftime('%H')), d.minute)
    return time_string

def date_human_format(d, country=None):
    month_day_of_week = d.strftime('%A, %B')
    month_day = '%s %s, %s' % (month_day_of_week, d.day, d.year)
    time_string = time_human_format(d, country=country)
    return '%s - %s' % (month_day, time_string)

def duration_human_format(d1, d2, country=None):
    first_date = date_human_format(d1)
    if d2:
        if (d2 - d1) > datetime.timedelta(hours=24):
            second_date = date_human_format(d2, country)
        else:
            second_date = time_human_format(d2, country)
        return "%s to %s" % (first_date, second_date)
    else:
        return first_date    
