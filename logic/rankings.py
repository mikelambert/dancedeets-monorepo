import datetime

from google.appengine.ext import db
from mapreduce import operation as op

from events import tags

# location is a city in cities.py
# time_period is one of ALL_TIME, LAST_MONTH, LAST_WEEK
# dance_style is one of tags.CHOREO_EVENT, tags.FREESTYLE_EVENT, None

LAST_WEEK = 'LAST_WEEK'
LAST_MONTH = 'LAST_MONTH'
ALL_TIME = 'ALL_TIME'

TIME_PERIODS = [
    LAST_WEEK,
    LAST_MONTH,
    ALL_TIME,
]

ANY_STYLE = 'ANY_STYLE'

def get_time_periods(timestamp):
    if timestamp < datetime.datetime.now() - datetime.timedelta(days=7):
        yield LAST_WEEK
    if timestamp < datetime.datetime.now() - datetime.timedelta(days=31):
        yield LAST_MONTH
    yield ALL_TIME

def get_dance_styles(dbevent):
    if tags.FREESTYLE_EVENT in dbevent.search_tags:
        yield tags.FREESTYLE_EVENT
    if tags.CHOREO_EVENT in dbevent.search_tags:
        yield tags.CHOREO_EVENT
    yield ANY_STYLE

def process(dbevent):
    for region in dbevent.search_regions:
        for time_period in get_time_periods(dbevent.creation_time or dbevent.start_time):
            for dance_style in get_dance_styles(dbevent):
                yield op.counters.Increment("%s/%s/%s" % (region, time_period, dance_style))

