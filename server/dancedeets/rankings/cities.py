import logging

from google.appengine.ext import db

from dancedeets import geohash
from dancedeets.loc import geohash_math
from dancedeets.loc import math
from dancedeets.loc import names
from dancedeets.util import runtime

CITY_GEOHASH_PRECISIONS = range(
    geohash_math.get_geohash_bits_for_km(1500),
    geohash_math.get_geohash_bits_for_km(50) + 1,
)

# The km of distance to nearest "scene" a user will identify with
# We group events into cities by NEARBY_DISTANCE_KM/2,
# then later everything expands by NEARBY_DISTANCE_KM in searching:
# - expand our search box by this
# - find people within this distance of our search box, too
NEARBY_DISTANCE_KM = 100


def get_nearby_cities(points, only_populated=False, country=None):
    # TODO(lambert): we should cache this entire function. use lowercase of location to determine cache key. Using DB cache too.
    logging.info("search location is %s", points)
    # rather than return the nearest city (Sunnyvale, San Jose, etc)
    # try to find the largest city within a certain range to give us good groupings for the "scene" name of a user/event.
    geohashes = geohash_math.get_all_geohashes_for(points)
    # This can return a bunch. In theory, it'd be nice to order by population, but that doesn't seem to work...
    if only_populated:
        cities = City.gql(
            "where geohashes in :geohashes and has_nearby_events = :nearby_events", geohashes=geohashes, nearby_events=True
        ).fetch(1000)
    else:
        cities = City.gql("where geohashes in :geohashes", geohashes=geohashes).fetch(1000)
    if points[0] != points[1]:
        cities = [x for x in cities if math.contains(points, (x.latitude, x.longitude))]
    if country:
        cities = [x for x in cities if x.country_name == country]
    return cities


def get_largest_cities(limit=5, country=None):
    if country:
        q = City.gql(
            "where has_nearby_events = :nearby_events and country_name = :country order by population desc",
            nearby_events=True,
            country=country
        )
    else:
        q = City.gql("where has_nearby_events = :nearby_events order by population desc", nearby_events=True)
    return q.fetch(limit=limit)


def get_largest_city(cities):
    if not cities:
        return City(city_name='Unknown')
    largest_nearby_city = max(cities, key=lambda x: x.population)
    return largest_nearby_city


class City(db.Model):
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

    def display_name(self):
        if self.city_name == 'Unknown':
            return self.city_name
        full_country = names.get_country_name(self.country_name)
        if self.country_name in ['US']:
            city_name = '%s, %s, %s' % (self.city_name, self.state_name, full_country)
        else:
            city_name = '%s, %s' % (self.city_name, full_country)
        return city_name

    def __repr__(self):
        return 'City(%s, %s, %s (%s, %s) Pop %s, hashes: %s)' % (
            self.city_name, self.state_name, self.country_name, self.latitude, self.longitude, self.population, self.geohashes
        )


def import_cities():
    # Download this file from http://download.geonames.org/export/dump/
    # Generally we import locally (to avoid 30sec servlet limits), then download-and-upload data:
    # appcfg.py download_data --application=dancedeets --kind="City" --url=http://127.0.0.1:8080/remote_api --filename=cities.db
    # appcfg.py upload_data --application=dancedeets --kind="City" --url=http://dancedeets.appspot.com/remote_api --filename=cities.db
    count = 0
    for line in open('cities15000.txt'):
        count += 1

        if not count % 1000:
            logging.info('Imported %s cities', count)
        # List of fields from http://download.geonames.org/export/dump/
        geonameid, name, asciiname, alternatenames, latitude, longitude, feature_class, feature_code, country_code, cc2, admin1_code, admin2_code, admin3_code, admin4_code, population, elevation, gtopo30, timezone, modification_date = line.split(
            '\t'
        )

        #if int(population) < 50000:
        #    print name, population
        #    continue
        city = City.get_or_insert(', '.join([asciiname, admin1_code, country_code]))
        city.city_name = asciiname
        city.state_name = admin1_code
        city.country_name = country_code
        city.latitude = float(latitude)
        city.longitude = float(longitude)
        city.population = int(population)
        city.geohashes = []
        if runtime.is_local_appengine():
            city.has_nearby_events = True
        for x in CITY_GEOHASH_PRECISIONS:
            city.geohashes.append(str(geohash.Geostring((float(latitude), float(longitude)), depth=x)))
        city.timezone = timezone
        city.put()
