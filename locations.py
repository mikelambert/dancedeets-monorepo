import base64
import hashlib
import hmac
import logging
import math
import urllib
import urllib2

import geohash

try:
    from django.utils import simplejson
except ImportError:
    import simplejson
try:
    import smemcache
except ImportError:
    smemcache = None
    pass

# http://en.wikipedia.org/wiki/Mile
MILES_COUNTRIES = ['UK', 'US']

# http://en.wikipedia.org/wiki/12-hour_clock
AMPM_COUNTRIES = ['AU', 'BD', 'CA', 'CO', 'EG', 'IN', 'MY', 'NZ', 'PK', 'PH', 'US']

LOCATION_EXPIRY = 24 * 60 * 60

class GeocodeException(Exception):
    pass

def _get_geocoded_data(address):
    unsigned_url_path = "/maps/api/geocode/json?%s" % urllib.urlencode(dict(address=address.encode('utf-8'), sensor='false', client='free-dancedeets'))
    private_key = 'zj918QnslsoOQHl4kLjv-ZCgsDE='
    decoded_key = base64.urlsafe_b64decode(private_key)
    signature = hmac.new(decoded_key, unsigned_url_path, hashlib.sha1)
    encoded_signature = base64.urlsafe_b64encode(signature.digest())

    url = "http://maps.google.com%s&signature=%s" % (unsigned_url_path, encoded_signature)

    results = urllib.urlopen(url).read()
    try:
        json_result = simplejson.loads(results)
    except simplejson.decoder.JSONDecodeError, e:
        logging.error("Error decoding json from %s: %s: %r", url, e, results)
        return None
    if json_result['status'] == 'ZERO_RESULTS':
        return None
    if json_result['status'] != 'OK':
        raise GeocodeException("Got unexpected status: %s" % json_result['status'])
    result = json_result['results'][0]
    return result


def _memcache_location_key(location):
    return 'GoogleMaps.%s' % location

def _raw_get_cached_geocoded_data(location):
    memcache_key = _memcache_location_key(location)
    geocoded_data = smemcache and smemcache.get(memcache_key)
    if not geocoded_data:
        geocoded_data = _get_geocoded_data(location)
        if smemcache:
            smemcache.set(memcache_key, geocoded_data, LOCATION_EXPIRY)
    return geocoded_data

def get_geocoded_location(address):
    if address:
        result = _raw_get_cached_geocoded_data(address)
    else:
        result = None
    geocoded_location = {}
    if result:
        geocoded_location['latlng'] = (result['geometry']['location']['lat'], result['geometry']['location']['lng'])
        geocoded_location['address'] = result['formatted_address']
    else:
        geocoded_location['latlng'] = None
        geocoded_location['address'] = None
    return geocoded_location

def get_country_and_state_for_location(location_name):
    result = _raw_get_cached_geocoded_data(location_name)
    if not result:
        return None
    states = [x['short_name'] for x in result['address_components'] if u'administrative_area_level_1' in x['types']]
    if len(states) != 1:
        raise GeocodeException("Found too many states: %s" % states)
    countries = [x['short_name'] for x in result['address_components'] if u'country' in x['types']]
    if len(countries) != 1:
        raise GeocodeException("Found too many countries: %s" % countries)
    return states[0], countries[0]

#TODO(lambert): at some point eliminate timezones.py and implement it using a proper geonames web service
# http://www.geonames.org/commercial-webservices.html
# timezone_url = "http://ws.geonames.org/timezoneJSON?lat=%s&lng=%s" % (lat, lng)

rad = math.pi / 180.0

def get_distance(lat1, lng1, lat2, lng2, use_km=False):
    dlat = (lat2-lat1) * rad
    dlng = (lng2-lng1) * rad
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
        math.cos(lat1 * rad) * math.cos(lat2 * rad) * 
        math.sin(dlng/2) * math.sin(dlng/2))
    circum = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
    if use_km:
        radius = 6371 # km
    else:
        radius = 3959 # miles
    distance = radius * circum
    return distance

def get_lat_lng_offsets(lat, lng, km):
    miles = km_in_miles(km)
    miles_per_nautical_mile = 1.15078
    lat_range = miles / (miles_per_nautical_mile * 60.0)
    lng_range = miles / (math.cos(lat * rad) * miles_per_nautical_mile * 60.0)
    return lat_range, lng_range

circumference_of_earth = 40000 # km
def get_geohash_bits_for_km(km):
    if km < min_box_size:
        return max_geohash_bits
    geohash_bits = int(math.ceil(-math.log(1.0 * km / circumference_of_earth) / math.log(2)))
    return geohash_bits

min_box_size = 200 # km
max_geohash_bits = get_geohash_bits_for_km(min_box_size)
# max_geohash_bits should be 8, which is reasonable compared to 32 possible for complete geohashing


one_over_sqrt_two = 1.0 / math.sqrt(2.0)
# to understand why we need circle_corners, see the BACKGROUND of:
# http://github.com/davetroy/geohash-js
circle_corners = [
    (-1, -1),
    (-1, +1),
    (+1, -1),
    (+1, +1),    (-one_over_sqrt_two, -one_over_sqrt_two),
    (-one_over_sqrt_two, +one_over_sqrt_two),
    (+one_over_sqrt_two, -one_over_sqrt_two),
    (+one_over_sqrt_two, +one_over_sqrt_two),
]
def get_all_geohashes_for(lat, lng, km):
    # We subtract one in an attempt to get less geohashes below (by using a larger search area),
    # but be aware we still risk having at most 9 geohashes in a worst-case edge-border
    # 90miles in NY = 2 geohashes
    # 90miles in SF = 6 geohashes
    precision = get_geohash_bits_for_km(km) - 1
    lat_range, lng_range = get_lat_lng_offsets(lat, lng, km)
    geohashes = set()
    for mult_lat, mult_lng in circle_corners:
        new_lat = lat + mult_lat*lat_range
        new_lng = lng + mult_lng*lng_range
        geohashes.add(str(geohash.Geostring((new_lat, new_lng), depth=precision)))
    return list(geohashes)

def miles_in_km(miles):
    return miles * 1.609344
def km_in_miles(km):
    return km * 0.6213712

