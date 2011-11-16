import datetime
import logging

import smemcache

from google.appengine.ext import db
from mapreduce import control
from mapreduce import model
from mapreduce import operation as op

from events import cities
from events import users
import locations

EVENT_FOR_CITY_RANKING = 'CITY_EVENT_RANKING'
USER_FOR_CITY_RANKING = 'CITY_USER_RANKING'
EVENT_FOR_USER_RANKING = 'EVENT_USER_RANKING'
USER_FOR_USER_RANKING = 'USER_USER_RANKING'

# location is a city in cities.py
# time_period is one of ALL_TIME, LAST_MONTH, LAST_WEEK

LAST_WEEK = 'LAST_WEEK'
LAST_MONTH = 'LAST_MONTH'
ALL_TIME = 'ALL_TIME'

TIME_PERIODS = [
    ALL_TIME,
    LAST_MONTH,
    LAST_WEEK,
]

string_translations = {
    ALL_TIME: 'all time',
    LAST_MONTH: 'last month',
    LAST_WEEK: 'last week',
}

def get_time_periods(timestamp):
    if timestamp > datetime.datetime.now() - datetime.timedelta(days=7):
        yield LAST_WEEK
    if timestamp > datetime.datetime.now() - datetime.timedelta(days=31):
        yield LAST_MONTH
    yield ALL_TIME

def make_key_name(key_name, **kwargs):
    return '%s/%s' % (key_name, '/'.join('%s=%s' % (k, v) for (k, v) in kwargs.iteritems()))

def count_event_for_city(dbevent):
    #TODO(lambert): store largest_city in the event
    if not dbevent.start_time: # deleted event, don't count
        return
    city = dbevent.city_name
    for time_period in get_time_periods(dbevent.creation_time or dbevent.start_time):
        yield op.counters.Increment(make_key_name("City", city=city, time_period=time_period))

def count_user_for_city(user):
    #TODO(lambert): store largest_city in the user
    user_city = cities.get_largest_nearby_city_name(user.location)
    for time_period in get_time_periods(user.creation_time):
        yield op.counters.Increment(make_key_name("City", city=user_city, time_period=time_period))

def begin_ranking_calculations():
    #TODO(lambert): move these into mapreduce.yaml, and expose them via a simple /XX API that we can trigger as needed
    control.start_map(
        name='Compute City Rankings by Events',
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec='logic.rankings.count_event_for_city',
        mapper_parameters={'entity_kind': 'events.eventdata.DBEvent'},
        queue_name='slow-queue',
        _app=EVENT_FOR_CITY_RANKING,
    )
    #TODO(lambert): Make the above have a done callback triggering this one:
    control.start_map(
        name='Compute City Rankings by Users',
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec='logic.rankings.count_user_for_city',
        mapper_parameters={'entity_kind': 'events.users.User'},
        queue_name='slow-queue',
        _app=USER_FOR_CITY_RANKING,
    )
    #TODO(lambert): move this into a /done callback on the above two
    compute_summary(expiry=5*60) # 5 minutes


TOTALS_KEY = 'StatTotals'
TOTALS_EXPIRY = 6*3600
def retrieve_summary():
    totals = smemcache.get(TOTALS_KEY)
    if not totals:
        totals = compute_summary()
    return totals

def compute_summary(expiry=TOTALS_EXPIRY):
    # IN PROGRESS
    event_rankings = get_city_by_event_rankings()
    if event_rankings:
        total_events = compute_sum(event_rankings, ALL_TIME)
    else:
        total_events = 0
    user_rankings = get_city_by_user_rankings()
    if user_rankings:
        total_users = compute_sum(user_rankings, ALL_TIME)
    else:
        total_users = 0
    event_sorted_rankings = get_thing_ranking(event_rankings, ALL_TIME)
    user_sorted_rankings = get_thing_ranking(user_rankings, ALL_TIME)

    # save
    totals = dict(total_events=total_events, total_users=total_users)
    smemcache.set(TOTALS_KEY, totals, expiry)

    return totals

def parse_key_name(full_key_name):
    if '/' not in full_key_name:
        return None, {}
    key_name, kwargs_string = full_key_name.split('/', 1)
    try:
        kwargs = dict(kv.split('=')  for kv in kwargs_string.split('/'))
    except ValueError:
        return None, {}
    return key_name, kwargs

def _get_counter_map_for_ranking(ranking):
    mapreduce_states = model.MapreduceState.gql('WHERE result_status = :result_status AND app_id = :app_id ORDER BY start_time DESC', result_status='success', app_id=ranking).fetch(1)
    if not mapreduce_states:
        return None
    final_counter_map = mapreduce_states[0].counters_map.counters
    return final_counter_map

def _group_cities_time_period(final_counter_map):
    cities = {}
    for k, counter in final_counter_map.iteritems():
        prefix, kwargs = parse_key_name(k)
        if prefix != 'City':
            continue
        cities.setdefault(kwargs['city'], {})[kwargs['time_period']] = counter
    return cities

def _group_users_time_period(final_counter_map, city):
    users = {}
    for k, counter in final_counter_map.iteritems():
        prefix, kwargs = parse_key_name(k)
        if prefix != 'User':
            continue
        if city and kwargs['city'] != city:
            continue
        users.setdefault(kwargs['user'], {})[kwargs['time_period']] = counter
    return users

def get_city_by_event_rankings():
    final_counter_map = _get_counter_map_for_ranking(EVENT_FOR_CITY_RANKING)
    if not final_counter_map:
        return None
    cities = _group_cities_time_period(final_counter_map)
    return cities

def get_city_by_user_rankings():
    final_counter_map = _get_counter_map_for_ranking(USER_FOR_CITY_RANKING)
    if not final_counter_map:
        return None
    cities = _group_cities_time_period(final_counter_map)
    return cities

def compute_sum(all_rankings, time_period):
    total_count = 0
    for city, times in all_rankings.iteritems():
        count = times.get(time_period, {})
        total_count += count
    return total_count

def compute_city_template_rankings(all_rankings, time_period, use_url=True):
    city_ranking = []
    for city, times in all_rankings.iteritems():
        if city == 'Unknown':
            continue
        count = times.get(time_period, {})
        if count:
            if use_url:
                url = '/city/%s' % city
            else:
                url = None
            city_ranking.append(dict(city=city, count=count, url=url))
    city_ranking = sorted(city_ranking, key=lambda x: -x['count'])
    return city_ranking

def get_thing_ranking(all_rankings, time_period):
    if not all_rankings:
        return []
    thing_ranking = []
    for thing, times in all_rankings.iteritems():
        if thing == 'Unknown':
            continue
        count = times.get(time_period, {})
        if count:
            thing_ranking.append(dict(key=thing, count=count))
    thing_ranking = sorted(thing_ranking, key=lambda x: -x['count'])
    return thing_ranking

def top_n_with_selected(thing_ranking, selected_name, group_size=3):
    def sel(x):
        return x['key'] == str(selected_name)
    selected_indices = [i for (i, x) in enumerate(thing_ranking) if sel(x)]
    if selected_indices:
        index = selected_indices[0]
        min_index = index - group_size/2
        max_index = index + group_size/2
        if min_index+1 <= group_size:
            group_size = max(max_index, group_size)
            selected_n = []
        else:
            selected_n = [(min_index+i+1, sel(x), x) for (i, x) in enumerate(thing_ranking[min_index:max_index+1])]
    else:
        selected_n = []
    top_n = [(i+1, sel(x), x) for (i, x) in enumerate(thing_ranking[:group_size])]
    return top_n, selected_n
