import json
import logging
import math

import geohash
from loc import gmaps
from loc import gmaps_bwcompat
from loc import gmaps_cached
from loc import math as loc_math

# http://en.wikipedia.org/wiki/Mile
MILES_COUNTRIES = ['UK', 'US']

LOCATION_EXPIRY = 24 * 60 * 60

def get_location_bounds(address, distance_in_km):
    if not address:
        return None, None
    geocode = gmaps.parse_geocode(gmaps_bwcompat.fetch_raw(address=address))
    if not geocode:
        return None, None
    northeast, southwest = geocode.latlng_bounds()

    logging.info("1 NE %s, SW %s", northeast, southwest)

    offsets_northeast = loc_math.get_lat_lng_offsets(northeast, distance_in_km)
    offsets_southwest = loc_math.get_lat_lng_offsets(southwest, distance_in_km)

    def add_latlngs(x, y):
        return (x[0] + y[0], x[1] + y[1])
    def sub_latlngs(x, y):
        return (x[0] - y[0], x[1] - y[1])
    northeast = add_latlngs(northeast, offsets_northeast)
    southwest = sub_latlngs(southwest, offsets_southwest)

    logging.info("2 NE %s, SW %s", northeast, southwest)

    return southwest, northeast # ordered more negative to more positive

def get_name(address=None, latlng=None):
    geocode = gmaps.parse_geocode(gmaps_bwcompat.fetch_raw(address=address, latlng=latlng))
    if not geocode:
        return None
    return _get_name(geocode.json_data)

def get_name_and_latlng(address=None, latlng=None):
    geocode = gmaps.parse_geocode(gmaps_bwcompat.fetch_raw(address=address, latlng=latlng))
    if not geocode:
        return None
    latlng = geocode.latlng()
    return _get_name(geocode.json_data), latlng

def get_latlng(address=None, latlng=None):
    geocode = gmaps.parse_geocode(gmaps_bwcompat.fetch_raw(address=address, latlng=latlng))
    if not geocode:
        return None
    return geocode.latlng()

def get_country_for_location(address=None, latlng=None, long_name=False):
    geocode = gmaps.parse_geocode(gmaps_bwcompat.fetch_raw(address=address, latlng=latlng))
    return geocode.country(long=long_name)

def _get_name(result):
    def get(name, long=True):
        components = [x[long and 'long_name' or 'short_name'] for x in result['address_components'] if name in x['types']]
        # Sometimes we see this, so return both 
        #{
        #  "long_name" : "Naka Ward",
        #  "short_name" : "Naka Ward",
        #  "types" : [ "locality", "political" ]
        #},
        #{
        #  "long_name" : "Nagoya",
        #  "short_name" : "Nagoya",
        #  "types" : [ "locality", "political" ]
        #},
        return components
        
    city_parts = []
    # TODO(lambert): Things to test and verify:
    # Bay Area, San Francisco, Brooklyn, New York, Tokyo, Osaka/Shibuya, Europe/Asia, The Haight
    city_parts.extend(get('locality') or get('sublocality') or get('administrative_area_level_3') or get('administrative_area_level_2') or get('colloquial_area'))
    country = get('country')
    if country:
        if country == ['United States']:
            city_parts.extend(get('administrative_area_level_1', long=False))
            city_parts.extend(get('country', long=False))
        else:
            city_parts.extend(get('administrative_area_level_1', long=False))
            city_parts.extend(country)
    else:
        if get('continent'):
            city_parts.extend(get('continent'))
        else:
            city_parts.extend(get('natural_feature'))

    city_name = ', '.join(x for x in city_parts if x)

    if not city_name:
        logging.warning("Could not get city for geocode results: %s", result)
    return city_name

circumference_of_earth = 40000.0 # km
def get_geohash_bits_for_km(km):
    if km < min_box_size:
        return max_geohash_bits
    geohash_bits = int(math.ceil(-math.log(1.0 * km / circumference_of_earth) / math.log(2)))
    return geohash_bits

def get_km_for_geohash_bits(precision):
    km = circumference_of_earth * math.pow(2, -precision)
    return km

min_box_size = 200 # km
max_geohash_bits = get_geohash_bits_for_km(min_box_size)
# max_geohash_bits should be 8, which is reasonable compared to 32 possible for complete geohashing


def get_all_geohashes_for(bounds, precision=None):
    if not precision:
        # We subtract one in an attempt to get less geohashes below (by using a larger search area),
        # but be aware we still risk having at most 5 geohashes in a worst-case edge-border
        # 90miles in NY = 2 geohashes
        # 90miles in SF = 3 geohashes
        km = loc_math.get_distance(bounds[0], bounds[1], use_km=True)
        precision = get_geohash_bits_for_km(km) - 1

    center = (
        (bounds[0][0] + bounds[1][0]) / 2,
        (bounds[0][1] + bounds[1][1]) / 2
    )

    # to understand why this is necessary, see the BACKGROUND of:
    # https://github.com/davetroy/geohash-js/blob/master/README
    pinpoints = [
        center,
        bounds[0],
        bounds[1],
        (bounds[0][0], bounds[1][1]),
        (bounds[1][0], bounds[0][1]),
    ]
    geohashes = set()
    for point in pinpoints:
        geohashes.add(str(geohash.Geostring(point, depth=precision)))
    return list(geohashes)


