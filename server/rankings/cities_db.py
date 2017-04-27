import logging
import sqlite3

FILENAME = 'rankings/cities.db'

connection = sqlite3.connect(FILENAME)
cursor = connection.cursor()

"""
class City(object):
    def __init__(self)
    created_date = db.DateTimeProperty(auto_now_add=True)

    city_name = db.StringProperty()
    state_name = db.StringProperty(indexed=False)
    country_name = db.StringProperty()
    latitude = db.FloatProperty(indexed=False)
    longitude = db.FloatProperty(indexed=False)
    population = db.IntegerProperty()
    timezone = db.StringProperty()
    geohashes = db.StringListProperty()

    # This indicates whether any events are "tagged" against this City
    # This can be used to filter out unnecessary cities in searches that don't have events/people associated with them
    has_nearby_events = db.BooleanProperty()
"""

def get_nearby_cities(points, country=None):
    # TODO(lambert): we should cache this entire function. use lowercase of location to determine cache key. Using DB cache too.
    logging.info("search location is %s", points)
    values = (points[0][0], points[1][0], points[0][1], points[1][1])
    query = ''
    if country:
        values = tuple(country, *values)
        query = ' and country_name = ?',
    cursor.execute('select * from City where ? < latitude and latitude < ? and ? < longitude and longitude < ? %s order by population desc' % query, values)
    results = cursor.fetchall()
    print results
    return results
"""
def get_largest_cities(limit=5, country=None):
    if country:
        q = City.gql("where has_nearby_events = :nearby_events and country_name = :country order by population desc", nearby_events=True, country=country)
    else:
        q = City.gql("where has_nearby_events = :nearby_events order by population desc", nearby_events=True)
    return q.fetch(limit=limit)

def get_largest_city(cities):
    if not cities:
        return City(city_name='Unknown')
    largest_nearby_city = max(cities, key=lambda x: x.population)
    return largest_nearby_city

def get_largest_nearby_city_name(point):
    southwest, northeast = math.expand_bounds((point, point), NEARBY_DISTANCE_KM/2)
    cities = get_nearby_cities((southwest, northeast))
    city = get_largest_city(cities)
    return city.display_name()
"""
