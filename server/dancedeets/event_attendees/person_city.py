from collections import Counter
import json
import logging
import math

from dancedeets.util import sqlite_db


def _get_cities(person_ids):
    conn = sqlite_db.get_connection('pr_person_city')
    cursor = conn.cursor()

    query = 'SELECT top_cities from PRPersonCity where person_id in (%s)' % ','.join('?' * len(person_ids))
    params = list(person_ids)
    cursor.execute(query, params)
    cities = []
    for result in cursor.fetchall():
        top_cities = json.loads(result[0])
        cities.extend(top_cities)
    return cities


def _distance_between(a, b):
    #TODO: I think we need to start passing everything around as geoname_ids, to make this cheap/efficient, right?
    raise NotImplementedError()


def get_stddev_distance_for(person_ids, event_location):
    distances = [_distance_between(city, event_location) for city in _get_cities(person_ids)]
    stddev = math.sqrt(sum(x * x for x in distances) / len(distances))
    return stddev


def get_top_city_for(person_ids):
    counts = Counter()
    for city in _get_cities(person_ids):
        counts[city] += 1
    top_cities = sorted(counts, key=lambda x: -counts[x])
    for i, city in enumerate(top_cities[:3]):
        logging.info('Top City %s: %s (%s attendees)', i, city, counts[city])
    if top_cities:
        return top_cities[0]
    else:
        return None
