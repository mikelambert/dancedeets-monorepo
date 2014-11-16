import base64
import hashlib
import hmac
import json
import logging
import math
import urllib

import geohash

from google.appengine.ext import db
try:
    import smemcache
except ImportError:
    smemcache = None
    pass

# http://en.wikipedia.org/wiki/Mile
MILES_COUNTRIES = ['UK', 'US']

LOCATION_EXPIRY = 24 * 60 * 60

class GeocodeException(Exception):
    pass

def _get_geocoded_data(address=None, latlng=None):
    params = {}
    if address is not None:
        params['address'] = address.encode('utf-8')
    if latlng is not None:
        params['latlng'] = '%s,%s' % latlng
    assert params
    params['sensor'] = 'false'
    params['client'] = 'free-dancedeets'
    unsigned_url_path = "/maps/api/geocode/json?%s" % urllib.urlencode(params)
    private_key = 'zj918QnslsoOQHl4kLjv-ZCgsDE='
    decoded_key = base64.urlsafe_b64decode(private_key)
    signature = hmac.new(decoded_key, unsigned_url_path, hashlib.sha1)
    encoded_signature = base64.urlsafe_b64encode(signature.digest())

    url = "http://maps.google.com%s&signature=%s" % (unsigned_url_path, encoded_signature)

    logging.info('geocoding url: %s', url)
    results = urllib.urlopen(url).read()
    logging.info('geocoding results: %s', results)
    try:
        json_result = json.loads(results)
    except json.decoder.JSONDecodeError, e:
        raise GeocodeException("Error decoding json from %s: %s: %r" % (url, e, results))
    if json_result['status'] == 'ZERO_RESULTS':
        return ''
    if json_result['status'] != 'OK':
        raise GeocodeException("Got unexpected status: %s" % json_result['status'])
    result = json_result['results'][0]
    return result

class GeoCode(db.Model):
    address = property(lambda x: int(x.key().name()))
    json_data = db.TextProperty()


def _memcache_location_key(location):
    return 'GoogleMaps.%s' % location

def _geocode_key(address, latlng):
    assert address or latlng
    assert not (address and latlng)
    if address:
        return address
    else:
        return '%s,%s' % latlng

def _raw_get_cached_geocoded_data(address=None, latlng=None):
    if not address and not latlng:
        return {}
    geocode_key = _geocode_key(address, latlng)
    memcache_key = _memcache_location_key(geocode_key)
    geocoded_data = smemcache and smemcache.get(memcache_key)
    if geocoded_data is None:
        geocode = GeoCode.get_by_key_name(geocode_key)
        if geocode:
            try:
                geocoded_data = json.loads(geocode.json_data)
            except:
                logging.exception("Error decoding json data for geocode %r with latlng %s: %r", address, latlng, geocode.json_data)
        if geocoded_data is None:
            geocoded_data = _get_geocoded_data(address=address, latlng=latlng)

            geocode = GeoCode(key_name=geocode_key)
            geocode.json_data = json.dumps(geocoded_data)
            geocode.put()
        if smemcache:
            smemcache.set(memcache_key, geocoded_data, LOCATION_EXPIRY)
    return geocoded_data

def get_location_bounds(address, distance_in_km):
    if not address:
        return None, None
    result = _raw_get_cached_geocoded_data(address=address)

    def to_latlng(x):
        return x['lat'], x['lng']
    try:
        northeast = to_latlng(result['geometry']['viewport']['northeast'])
        southwest = to_latlng(result['geometry']['viewport']['southwest'])
    except TypeError as e:
        logging.error("Ungeocodable address %r gave result: %r", address, result)
        #TODO(lambert): do a better job returning these as errors to the user
        raise e

    logging.info("1 NE %s, SW %s", northeast, southwest)

    offsets_northeast = get_lat_lng_offsets(northeast, distance_in_km)
    offsets_southwest = get_lat_lng_offsets(southwest, distance_in_km)

    def add_latlngs(x, y):
        return (x[0] + y[0], x[1] + y[1])
    def sub_latlngs(x, y):
        return (x[0] - y[0], x[1] - y[1])
    northeast = add_latlngs(northeast, offsets_northeast)
    southwest = sub_latlngs(southwest, offsets_southwest)

    logging.info("2 NE %s, SW %s", northeast, southwest)

    return southwest, northeast # ordered more negative to more positive

def get_city_name(address=None, latlng=None):
    result = _raw_get_cached_geocoded_data(address=address, latlng=latlng)
    if not result:
        return None
    return _get_city_name(result)

def get_city_name_and_latlng(address=None, latlng=None):
    result = _raw_get_cached_geocoded_data(address=address, latlng=latlng)
    if not result:
        return None
    latlng = (float(result['geometry']['location']['lat']), float(result['geometry']['location']['lng']))
    return _get_city_name(result), latlng

def get_latlng(address=None, latlng=None):
    result = _raw_get_cached_geocoded_data(address=address, latlng=latlng)
    if not result:
        return None
    return (float(result['geometry']['location']['lat']), float(result['geometry']['location']['lng']))

def _get_city_name(result):
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
    city_parts.extend(get('locality') or get('sublocality') or get('administrative_area_level_3') or get('administrative_area_level_2'))
    country = get('country')
    if country == ['United States']:
        city_parts.extend(get('administrative_area_level_1', long=False))
        city_parts.extend(get('country', long=False))
    else:
        city_parts.extend(get('administrative_area_level_1', long=False))
        city_parts.extend(country)
    city_name = ', '.join(x for x in city_parts if x)

    if not city_name:
        logging.warning("Could not get city for geocode results: %s", result)
    return city_name

def get_country_for_location(location_name):
    result = _raw_get_cached_geocoded_data(address=location_name)
    if not result:
        return None
    countries = [x['short_name'] for x in result['address_components'] if u'country' in x['types']]
    if len(countries) == 0:
        raise GeocodeException("Found no countries for %s: %r" % (location_name, result))
    if len(countries) > 1:
        raise GeocodeException("Found too many countries for %s: %s" % (location_name, countries))
    return countries[0]

rad = math.pi / 180.0

def get_distance(latlng1, latlng2, use_km=False):
    dlat = (latlng2[0]-latlng1[0]) * rad
    dlng = (latlng2[1]-latlng1[1]) * rad
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
        math.cos(latlng1[0] * rad) * math.cos(latlng2[0] * rad) * 
        math.sin(dlng/2) * math.sin(dlng/2))
    circum = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
    if use_km:
        radius = 6371 # km
    else:
        radius = 3959 # miles
    distance = radius * circum
    return distance

def contains(bounds, latlng):
    lats_good = bounds[0][0] < latlng[0] < bounds[1][0]
    if bounds[0][1] < bounds[1][1]:
        lngs_good = bounds[0][1] < latlng[1] < bounds[1][1]
    else:
        lngs_good = bounds[0][1] < latlng[1] or latlng[1] < bounds[1][1]
    return lats_good and lngs_good

def get_lat_lng_offsets(latlng, km):
    miles = km_in_miles(km)
    miles_per_nautical_mile = 1.15078
    lat_range = miles / (miles_per_nautical_mile * 60.0)
    lng_range = miles / (math.cos(latlng[0] * rad) * miles_per_nautical_mile * 60.0)
    return lat_range, lng_range

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
        km = get_distance(bounds[0], bounds[1], use_km=True)
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

def miles_in_km(miles):
    return miles * 1.609344
def km_in_miles(km):
    return km * 0.6213712

