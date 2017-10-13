import logging
import sqlite3

from dancedeets.loc import math
from dancedeets.loc import names
from dancedeets.util import sqlite_db

TEST_FILENAME = 'dancedeets/geonames/cities_test.db'

# The km of distance to nearest "scene" a user will identify with
# We group events into cities by NEARBY_DISTANCE_KM/2,
# then later everything expands by NEARBY_DISTANCE_KM in searching:
# - expand our search box by this
# - find people within this distance of our search box, too
NEARBY_DISTANCE_KM = 100


def get_nearby_city(latlng, country=None):
    nearby_cities = get_nearby_cities(latlng, country=country)
    city = _get_largest_city(nearby_cities)
    return city


def get_current_city(latlng):
    for distance in [20, 100, 500]:
        nearby_cities = get_nearby_cities(latlng, distance=distance)
        if nearby_cities:
            closest_cities = sorted(nearby_cities, key=lambda x: -x.distance_to(latlng))
            return closest_cities[0]


def get_nearby_cities(latlng, country=None, distance=None):
    # We shrink it by two:
    # An event in Palo Alto could be thrown into a San Jose bucket
    # But an event in San Francisco, looking for "people who would go to SF event",
    # would want to include Palo Alto in its search radius....so would need to go 2x to San Jose
    # So instead of searching 200km in popular people for cities...let's try to be more specific about which person goes to which city
    distance = distance or NEARBY_DISTANCE_KM / 2
    southwest, northeast = math.expand_bounds((latlng, latlng), distance)
    nearby_cities = get_contained_cities((southwest, northeast), country=country)
    nearby_cities = [x for x in nearby_cities if x.closer_than(latlng, distance)]
    return nearby_cities


class City(object):
    def __init__(self, data):
        self.__dict__ = dict((x, data[x]) for x in data.keys())

    def display_name(self):
        if self is None:
            return 'Unknown'
        full_country = names.get_country_name(self.country_code)
        if self.country_code in ['US']:
            city_name = '%s, %s, %s' % (self.ascii_name, self.admin1_code, full_country)
        else:
            city_name = '%s, %s' % (self.ascii_name, full_country)
        return city_name

    def closer_than(self, latlng, distance):
        real_distance = self.distance_to(latlng)
        return real_distance < distance

    def distance_to(self, latlng):
        return math.get_distance(latlng, (self.latitude, self.longitude), use_km=True)


def lookup_city_from_geoname_id(geoname_id):
    connection = sqlite_db.get_connection('cities', TEST_FILENAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('select * from City where geoname_id = ?', (geoname_id,))
    return City(cursor.fetchone())


def get_contained_cities(points, country=None):
    logging.info("citiesdb search location is %s", points)
    values = [points[0][0], points[1][0], points[0][1], points[1][1]]
    query = ''
    if country:
        values += [country]
        query = ' and country_code = ?',
    connection = sqlite_db.get_connection('cities', TEST_FILENAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(
        'select * from City where ? < latitude and latitude < ? and ? < longitude and longitude < ? %s order by population desc' % query,
        values
    )
    results = cursor.fetchall()
    return [City(x) for x in results]


def get_largest_cities(limit=5, country=None):
    raise NotImplementedError()


def _get_largest_city(cities):
    if not cities:
        return None
    largest_nearby_city = max(cities, key=lambda x: x.population)
    return largest_nearby_city
