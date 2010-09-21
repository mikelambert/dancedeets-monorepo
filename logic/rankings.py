import datetime

from google.appengine.ext import db
from mapreduce import control
from mapreduce import model
from mapreduce import operation as op

from events import cities
from events import tags
from events import users
import locations

EVENT_RANKING = 'EVENT_RANKING'
USER_RANKING = 'USER_RANKING'

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

CHOREO_FAN = users.CHOREO_FAN
CHOREO_DANCER = users.CHOREO_DANCER
FREESTYLE_FAN = users.FREESTYLE_FAN
FREESTYLE_DANCER = users.FREESTYLE_DANCER
DANCE_FAN = 'DANCE_FAN'
DANCE_DANCER = 'DANCE_DANCER'

PEOPLES = [
    CHOREO_FAN,
    CHOREO_DANCER,
    FREESTYLE_FAN,
    FREESTYLE_DANCER,
    DANCE_FAN,
    DANCE_DANCER,
]

def get_time_periods(timestamp):
    if timestamp < datetime.datetime.now() - datetime.timedelta(days=7):
        yield LAST_WEEK
    if timestamp < datetime.datetime.now() - datetime.timedelta(days=31):
        yield LAST_MONTH
    yield ALL_TIME

def get_user_dance_styles(user):
    if user.freestyle == users.FREESTYLE_FAN:
        yield FREESTYLE_FAN
    elif user.freestyle == users.FREESTYLE_DANCER:
        yield FREESTYLE_FAN
        yield FREESTYLE_DANCER

    if user.choreo == users.CHOREO_FAN:
        yield CHOREO_FAN
    elif user.choreo == users.CHOREO_DANCER:
        yield CHOREO_FAN
        yield CHOREO_DANCER

    if user.choreo != users.CHOREO_APATHY and user.freestyle != users.FREESTYLE_APATHY:
        yield DANCE_FAN
        if user.choreo == users.CHOREO_DANCER or user.freestyle == users.FREESTYLE_DANCER:
            yield DANCE_DANCER

def get_event_dance_styles(dbevent):
    if tags.FREESTYLE_EVENT in dbevent.search_tags:
        yield FREESTYLE_STYLE
    if tags.CHOREO_EVENT in dbevent.search_tags:
        yield CHOREO_STYLE
    yield ANY_STYLE

def count_event(dbevent):
    for region in dbevent.search_regions:
        for time_period in get_time_periods(dbevent.creation_time or dbevent.start_time):
            for dance_style in get_event_dance_styles(dbevent):
                yield op.counters.Increment("%s/%s/%s" % (region, time_period, dance_style))

def count_user(user):
    latlng_user_location = locations.get_geocoded_location(user.location)['latlng']
    user_city = cities.get_closest_city(latlng_user_location[0], latlng_user_location[1])
    for time_period in get_time_periods(user.creation_time):
        for dance_style in get_user_dance_styles(user):
            yield op.counters.Increment("%s/%s/%s" % (user_city, time_period, dance_style))

def begin_ranking_calculations():
    control.start_map(
        name='Compute Event Rankings',
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec='logic.rankings.count_event',
        reader_parameters={'entity_kind': 'events.eventdata.DBEvent'},
        _app=EVENT_RANKING,
    )
    control.start_map(
        name='Compute User Rankings',
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec='logic.rankings.count_user',
        reader_parameters={'entity_kind': 'events.users.User'},
        _app=USER_RANKING,
    )

def get_event_rankings():
    mapreduce_states = model.MapreduceState.gql('WHERE result_status = :result_status AND app_id = :app_id ORDER BY start_time DESC', result_status='success', app_id=EVENT_RANKING).fetch(1)
    final_counter_map = mapreduce_states[0].counters_map.counters
    cities = {}
    for k, counter in final_counter_map.iteritems():
        if k.count('/') != 2:
            continue
        city, time_period, dance_style = k.split('/')
        cities.setdefault(city, {}).setdefault(time_period, {})[dance_style] = counter
    return cities

def get_user_rankings():
    mapreduce_states = model.MapreduceState.gql('WHERE result_status = :result_status AND app_id = :app_id ORDER BY start_time DESC', result_status='success', app_id=USER_RANKING).fetch(1)
    final_counter_map = mapreduce_states[0].counters_map.counters
    cities = {}
    for k, counter in final_counter_map.iteritems():
        if k.count('/') != 2:
            continue
        city, time_period, dance_style = k.split('/')
        cities.setdefault(city, {}).setdefault(time_period, {})[dance_style] = counter
    return cities

