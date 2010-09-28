import logging
import math

from google.appengine.ext import db

import geohash
import locations

CITY_GEOHASH_PRECISIONS = [4, 5, 6, 7]

def get_closest_city(location):
    latitude, longitude = locations.get_geocoded_location(location)['latlng']
    city_distance = lambda city: locations.get_distance(latitude, longitude, city.latitude, city.longitude, use_km=True)

    for precision in reversed(CITY_GEOHASH_PRECISIONS):
        geohashes = locations.get_all_geohashes_for(latitude, longitude, precision=precision)
        cities = City.gql("where geohashes in :geohashes", geohashes=geohashes).fetch(100)
        if cities:
            closest_city = min(cities, key=city_distance)
            logging.info("For user in %s, found %s cities for user with geohash precision=%s, closest city=%s", location, len(cities), precision, closest_city.key().name())
            if city_distance(closest_city) < 200:
                return closest_city
            else:
                logging.error("For user in %s, no city within 200km", location)
                return None

class City(db.Model):
    city_name = db.StringProperty()
    state_name = db.StringProperty()
    country_name = db.StringProperty()
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()
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

        if int(population) < 100000:
            continue
        city_geohash = str(geohash.Geostring((float(latitude), float(longitude)), depth=10))
        city = City.get_or_insert(', '.join([asciiname, admin1_code, country_code]))
        city.city_name = asciiname
        city.state_name = admin1_code
        city.country_name = country_code
        city.latitude = float(latitude)
        city.longitude = float(longitude)
        city.geohashes = []
        for x in CITY_GEOHASH_PRECISIONS:
            city.geohashes.append(str(geohash.Geostring((float(latitude), float(longitude)), depth=x)))
        city.timezone = timezone
        city.put()


