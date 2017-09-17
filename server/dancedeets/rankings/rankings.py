import datetime

from google.appengine.api import memcache

from mapreduce import control
from mapreduce import model
from mapreduce import operation as op

from loc import gmaps_api
from . import cities_db

EVENT_FOR_CITY_RANKING = 'CITY_EVENT_RANKING'
USER_FOR_CITY_RANKING = 'CITY_USER_RANKING'
EVENT_FOR_USER_RANKING = 'EVENT_USER_RANKING'
USER_FOR_USER_RANKING = 'USER_USER_RANKING'

# location is a city in cities/state/country
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
    if not dbevent.start_time:  # deleted event, don't count
        return
    if not dbevent.latitude or not dbevent.longitude:  # no-location event, don't count
        return
    city = dbevent.city_name
    for time_period in get_time_periods(dbevent.creation_time or dbevent.start_time):
        yield op.counters.Increment(make_key_name("City", city=city, time_period=time_period))


def count_user_for_city(user):
    user_city = user.city_name
    for time_period in get_time_periods(user.creation_time):
        yield op.counters.Increment(make_key_name("City", city=user_city, time_period=time_period))


def begin_ranking_calculations():
    #TODO(lambert): move these into mapreduce.yaml, and expose them via a simple /XX API that we can trigger as needed
    control.start_map(
        name='Compute City Rankings by Events',
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec='rankings.rankings.count_event_for_city',
        mapper_parameters={'entity_kind': 'events.eventdata.DBEvent'},
        queue_name='fast-queue',
        shard_count=16,
        _app=EVENT_FOR_CITY_RANKING,
    )
    #TODO(lambert): Make the above have a done callback triggering this one:
    control.start_map(
        name='Compute City Rankings by Users',
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec='rankings.rankings.count_user_for_city',
        mapper_parameters={'entity_kind': 'users.users.User'},
        queue_name='fast-queue',
        shard_count=16,
        _app=USER_FOR_CITY_RANKING,
    )
    #TODO(lambert): move this into a /done callback on the above two. use pipeline api?
    _compute_summary(expiry=5 * 60)  # 5 minutes


TOTALS_KEY = 'StatTotals'
TOTALS_EXPIRY = 6 * 3600


def retrieve_summary():
    totals = memcache.get(TOTALS_KEY)
    if not totals:
        totals = _compute_summary()
    return totals


def _compute_summary(expiry=TOTALS_EXPIRY):
    # IN PROGRESS
    event_rankings = get_city_by_event_rankings()
    if event_rankings:
        total_events = _compute_sum(event_rankings, ALL_TIME)
    else:
        total_events = 0
    user_rankings = get_city_by_user_rankings()
    if user_rankings:
        total_users = _compute_sum(user_rankings, ALL_TIME)
    else:
        total_users = 0

    # save
    totals = dict(total_events=total_events, total_users=total_users)
    memcache.set(TOTALS_KEY, totals, expiry)

    return totals


def _parse_key_name(full_key_name):
    if '/' not in full_key_name:
        return None, {}
    key_name, kwargs_string = full_key_name.split('/', 1)
    try:
        kwargs = dict(kv.split('=') for kv in kwargs_string.split('/'))
    except ValueError:
        return None, {}
    return key_name, kwargs


def _get_counter_map_for_ranking(ranking):
    mapreduce_states = model.MapreduceState.gql(
        'WHERE result_status = :result_status AND app_id = :app_id ORDER BY start_time DESC', result_status='success', app_id=ranking
    ).fetch(1)
    if not mapreduce_states:
        return None
    final_counter_map = mapreduce_states[0].counters_map.counters
    return final_counter_map


def _group_cities_time_period(final_counter_map):
    cities = {}
    for k, counter in final_counter_map.iteritems():
        prefix, kwargs = _parse_key_name(k)
        if prefix != 'City':
            continue
        cities.setdefault(kwargs['city'], {})[kwargs['time_period']] = counter
    return cities


def _group_users_time_period(final_counter_map, city):
    users = {}
    for k, counter in final_counter_map.iteritems():
        prefix, kwargs = _parse_key_name(k)
        if prefix != 'User':
            continue
        if city and kwargs['city'] != city:
            continue
        users.setdefault(kwargs['user'], {})[kwargs['time_period']] = counter
    return users


def get_city_by_event_rankings():
    final_counter_map = _get_counter_map_for_ranking(EVENT_FOR_CITY_RANKING)
    if not final_counter_map:
        return {}
    cities = _group_cities_time_period(final_counter_map)
    return cities


def get_city_by_user_rankings():
    final_counter_map = _get_counter_map_for_ranking(USER_FOR_CITY_RANKING)
    if not final_counter_map:
        return {}
    cities = _group_cities_time_period(final_counter_map)
    return cities


def _compute_sum(all_rankings, time_period):
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
    city_ranking = sorted(city_ranking, key=lambda x: (-x['count'], x['city']))
    return city_ranking
