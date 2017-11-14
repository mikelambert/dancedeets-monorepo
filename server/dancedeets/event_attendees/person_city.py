from collections import Counter
import json
import logging
import math

from dancedeets.rankings import cities_db
from dancedeets.util import sqlite_db


def _get_lol_cities(person_ids):
    conn = sqlite_db.get_connection('pr_person_city')
    cursor = conn.cursor()

    query = 'SELECT person_id, top_cities from PRPersonCity where person_id in (%s)' % ','.join('?' * len(person_ids))
    cursor.execute(query, person_ids)
    lol_cities = []
    found_person_ids = []
    for result in cursor.fetchall():
        found_person_ids.append(result[0])
        top_cities = [x for x in json.loads(result[1]) if x]
        lol_cities.append(top_cities)
    missing_ids = set(person_ids).difference(found_person_ids)
    logging.info("Missing ids we cannot find cities for: %s", missing_ids)
    return lol_cities


def _get_cities(person_ids):
    lol_cities = _get_lol_cities(person_ids)
    cities = []
    for top_cities in lol_cities:
        cities.extend(top_cities)
    return cities


def _distance_to(geoname_id, latlng):
    city = cities_db.lookup_city_from_geoname_ids([geoname_id])[0]
    distance = city.distance_to(latlng)
    return distance


def get_nonlocal_fraction(person_ids, center_latlng):
    data = get_data_fields(person_ids, center_latlng)
    if not data:
        return 0
    nonlocal_fraction = 1.0 * (data['total_known_people'] - data['count_histogram'][0]) / data['total_known_people']
    return nonlocal_fraction


def get_data_fields(person_ids, center_latlng):
    distances = []
    for top_cities in _get_lol_cities(person_ids):
        if top_cities:
            min_distance = min([_distance_to(x, center_latlng) for x in top_cities])
            distances.append(min_distance)

    if not len(distances):
        return None

    avg = sum(distances) / len(distances)
    rms = math.sqrt(sum(x * x for x in distances) / len(distances))
    local = len([x for x in distances if x < 200])
    regional = len([x for x in distances if x >= 200 and x < 2000])
    continental = len([x for x in distances if x >= 2000 and x < 6000])
    intercontinental = len([x for x in distances if x >= 6000])

    data = {
        'distance_average': int(avg),
        'distance_rms': int(rms),
        'total_attending_maybe_people': len(person_ids),
        'total_known_people': len(distances),
        'count_histogram': (local, regional, continental, intercontinental),
    }
    return data


def get_top_geoname_for(person_ids):
    counts = Counter()
    total_count = 0
    for city in _get_cities(person_ids):
        counts[city] += 1
        total_count += 1
    top_cities = sorted(counts, key=lambda x: -counts[x])
    for i, geoname_id in enumerate(top_cities[:3]):
        cities = cities_db.lookup_city_from_geoname_ids([geoname_id])
        if cities:
            city = cities[0]
            logging.info('Top City %s: %s (%s attendees)', i, city.display_name(), counts[geoname_id])
        else:
            logging.error('Failed to find city for geoname %s', geoname_id)
    if top_cities:
        top_geoname_id = top_cities[0]
        city_count = counts[top_geoname_id]
        # More than 10%, and must have at least 3 people
        if city_count >= 3 and city_count >= total_count * 0.1:
            return top_geoname_id
    return None


def get_top_city_for(person_ids):
    top_geoname_id = get_top_geoname_for(person_ids)
    if top_geoname_id:
        city = cities_db.lookup_city_from_geoname_ids([top_geoname_id])[0]
        return city.display_name()
    else:
        False
