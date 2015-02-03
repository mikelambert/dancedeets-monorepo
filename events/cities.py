import logging

from google.appengine.ext import db

import geohash
import locations
from util import abbrev

CITY_GEOHASH_PRECISIONS = range(
    locations.get_geohash_bits_for_km(1500),
    locations.get_geohash_bits_for_km(200) + 1,
)

NEARBY_DISTANCE_KM = 100 # km of distance to nearest "scene" a user will identify with

def get_largest_nearby_city_name(location):
    # TODO(lambert): we should cache this entire function. use lowercase of location to determine cache key. Using DB cache too.
    logging.info("location is %s", location)
    # rather than return the nearest city (Sunnyvale, San Jose, etc)
    # try to find the largest city within a certain range to give us good groupings for the "scene" name of a user/event.
    point = locations.get_latlng(address=location)
    if point is None:
        return "Unknown"
    geohashes = locations.get_all_geohashes_for((point, point), precision=locations.get_geohash_bits_for_km(NEARBY_DISTANCE_KM))
    cities = City.gql("where geohashes in :geohashes", geohashes=geohashes).fetch(100)
    cities = [x for x in cities if locations.get_distance(point, (x.latitude, x.longitude), use_km=True) < NEARBY_DISTANCE_KM]
    if not cities:
        return "Unknown"
    largest_nearby_city = max(cities, key=lambda x: x.population)
    city_name = '%s, %s' % (largest_nearby_city.city_name, abbrev.countries_abbrev2full[largest_nearby_city.country_name])
    if city_name == 'San Jose, United States':
        city_name = 'San Francisco, United States'
    if city_name == 'San Francisco, United States':
        city_name = 'San Francisco Bay Area, United States'
    if city_name == 'Tijuana, Mexico':
        city_name = 'San Diego, United States'
    city_name = city_name.replace("Taiwan, Province of China", "Taiwan")
    return city_name

class City(db.Model):
    city_name = db.StringProperty()
    state_name = db.StringProperty()
    country_name = db.StringProperty()
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
    population = db.IntegerProperty()
    timezone = db.StringProperty()
    geohashes = db.StringListProperty()

def import_cities():
    # Download this file from http://download.geonames.org/export/dump/
    # Generally we import locally (to avoid 30sec servlet limits), then download-and-upload data:
    # appcfg.py download_data --application=dancedeets --kind="City" --url=http://127.0.0.1:8080/remote_api --filename=cities.db
    # appcfg.py upload_data --application=dancedeets --kind="City" --url=http://dancedeets.appspot.com/remote_api --filename=cities.db
    for line in open('cities15000.txt'):
        # List of fields from http://download.geonames.org/export/dump/
        geonameid, name, asciiname, alternatenames, latitude, longitude, feature_class, feature_code, country_code, cc2, admin1_code, admin2_code, admin3_code, admin4_code, population, elevation, gtopo30, timezone, modification_date = line.split('\t')

        if int(population) < 50000:
            continue
        city = City.get_or_insert(', '.join([asciiname, admin1_code, country_code]))
        city.city_name = asciiname
        city.state_name = admin1_code
        city.country_name = country_code
        city.latitude = float(latitude)
        city.longitude = float(longitude)
        city.population = int(population)
        city.geohashes = []
        for x in CITY_GEOHASH_PRECISIONS:
            city.geohashes.append(str(geohash.Geostring((float(latitude), float(longitude)), depth=x)))
        city.timezone = timezone
        city.put()


