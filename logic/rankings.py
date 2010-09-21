import datetime

from google.appengine.ext import db
from mapreduce import model

from events import tags

# location is a city in cities.py
# time_period is one of ALL_TIME, LAST_MONTH, LAST_WEEK
# dance_style is one of tags.CHOREO_EVENT, tags.FREESTYLE_EVENT, None

LAST_WEEK = 'LAST_WEEK'
LAST_MONTH = 'LAST_MONTH'
ALL_TIME = 'ALL_TIME'

TIME_PERIODS = [
    ALL_TIME,
    LAST_MONTH,
    LAST_WEEK,
]

FREESTYLE_STYLE = tags.FREESTYLE_EVENT
CHOREO_STYLE = tags.CHOREO_EVENT
ANY_STYLE = 'ANY_STYLE'

STYLES = [
    ANY_STYLE,
    FREESTYLE_STYLE,
    CHOREO_STYLE,
]

def get_time_periods(timestamp):
    if timestamp < datetime.datetime.now() - datetime.timedelta(days=7):
        yield LAST_WEEK
    if timestamp < datetime.datetime.now() - datetime.timedelta(days=31):
        yield LAST_MONTH
    yield ALL_TIME

def get_dance_styles(dbevent):
    if tags.FREESTYLE_EVENT in dbevent.search_tags:
        yield FREESTYLE_STYLE
    if tags.CHOREO_EVENT in dbevent.search_tags:
        yield CHOREO_STYLE
    yield ANY_STYLE

def process(dbevent):
    for region in dbevent.search_regions:
        for time_period in get_time_periods(dbevent.creation_time or dbevent.start_time):
            for dance_style in get_dance_styles(dbevent):
                yield op.counters.Increment("%s/%s/%s" % (region, time_period, dance_style))

def get_rankings():
    mapreduce_states = model.MapreduceState.gql('WHERE result_status = :result_status ORDER BY start_time DESC', result_status='success').fetch(1)
    final_counter_map = mapreduce_states[0].counters_map.counters
    cities = {}
    for k, counter in final_counter_map.iteritems():
        if k.count('/') != 2:
            continue
        city, time_period, dance_style = k.split('/')
        cities.setdefault(city, {}).setdefault(time_period, {})[dance_style] = counter
    return cities

