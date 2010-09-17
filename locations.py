import base64
import hashlib
import hmac
import logging
import math
import urllib
import urllib2

from google.appengine.ext.appstats import recording
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
    recording.recorder.record_custom_event('googlemaps-fetch')
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
    result = _raw_get_cached_geocoded_data(address)
    geocoded_location = {}
    if result:
        geocoded_location['latlng'] = (result['geometry']['location']['lat'], result['geometry']['location']['lng'])
        geocoded_location['address'] = result['formatted_address']
    else:
        geocoded_location['latlng'] = None
        geocoded_location['address'] = None
    return geocoded_location

def get_distance(lat1, lng1, lat2, lng2, use_km=False):
    deg_per_rad = 57.2957795
    dlat = (lat2-lat1) / deg_per_rad
    dlng = (lng2-lng1) / deg_per_rad
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
        math.cos(lat1 / deg_per_rad) * math.cos(lat2 / deg_per_rad) * 
        math.sin(dlng/2) * math.sin(dlng/2))
    circum = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
    if use_km:
        radius = 6371 # km
    else:
        radius = 3959 # miles
    distance = radius * circum
    return distance

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

def miles_in_km(miles):
    return miles * 1.609344

