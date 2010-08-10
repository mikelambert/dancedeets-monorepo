import base64
import hashlib
import hmac
import logging
import math
import urllib
import urllib2

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
    unsigned_url_path = "/maps/api/geocode/json?%s" % urllib.urlencode(dict(address=address, sensor='false', client='free-dancedeets'))
    private_key = 'zj918QnslsoOQHl4kLjv-ZCgsDE='
    decoded_key = base64.urlsafe_b64decode(private_key)
    signature = hmac.new(decoded_key, unsigned_url_path, hashlib.sha1)
    encoded_signature = base64.urlsafe_b64encode(signature.digest())

    url = "http://maps.google.com%s&signature=%s" % (unsigned_url_path, encoded_signature)

    results = urllib.urlopen(url).read()
    try:
        json_result = simplejson.loads(results)
    except simplejson.decoder.JSONDecodeError, e:
        logging.error("Error decoding json: %s: %s", e, results)
        return None
    if json_result['status'] == 'ZERO_RESULTS':
        return None
    if json_result['status'] != 'OK':
        raise GeocodeException("Got unexpected status: %s" % json_result['status'])
    result = json_result['results'][0]
    return result


def memcache_location_key(location):
  return 'Location.%s' % location

def _raw_get_geocoded_location(address):
    result = _get_geocoded_data(address)
    geocoded_location = {}
    if result:
        geocoded_location['latlng'] = (result['geometry']['location']['lat'], result['geometry']['location']['lng'])
        geocoded_location['address'] = result['formatted_address']
    else:
        geocoded_location['latlng'] = None
        geocoded_location['address'] = address
    return geocoded_location

def get_geocoded_location(location):
  memcache_key = memcache_location_key(location)
  geocoded_location = smemcache and smemcache.get(memcache_key)
  if not geocoded_location:
    geocoded_location = _raw_get_geocoded_location(location)
    if smemcache:
      smemcache.set(memcache_key, geocoded_location, LOCATION_EXPIRY)
  return geocoded_location



def get_distance(lat1, lng1, lat2, lng2, use_km=False):
    deg_to_rad = 57.2957795
    dlat = (lat2-lat1) / deg_to_rad
    dlng = (lng2-lng1) / deg_to_rad
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
        math.cos(lat1 / deg_to_rad) * math.cos(lat2 / deg_to_rad) * 
        math.sin(dlng/2) * math.sin(dlng/2))
    circum = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
    if use_km:
        radius = 3959 # miles
    else:
        radius = 6371 # km
    distance = radius * circum
    return distance


def _memcache_country_key(location_name):
  return 'FacebookLocation.%s' % location_name

def _raw_get_country_for_location(location_name):
    result = _get_geocoded_data(location_name)
    if not result:
        return None
    countries = [x['short_name'] for x in result['address_components'] if u'country' in x['types']]
    if len(countries) != 1:
        raise GeocodeException("Found too many countries: %s" % countries)
    return countries[0]

def get_country_for_location(location_name):
  memcache_key = _memcache_country_key(location_name)
  country = smemcache and smemcache.get(memcache_key)
  if not country:
    country = _raw_get_country_for_location(location_name)
    if smemcache:
      smemcache.set(memcache_key, country, LOCATION_EXPIRY)
  return country

