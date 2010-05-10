import gmaps
from google.appengine.api import memcache

MEMCACHE_EXPIRY = 24 * 3600

# http://en.wikipedia.org/wiki/Mile
MILES_COUNTRIES = ['UK', 'US']

# http://en.wikipedia.org/wiki/12-hour_clock
AMPM_COUNTRIES = ['AU', 'BD', 'CA', 'CO', 'EG', 'IN', 'MY', 'NZ', 'PK', 'PH', 'US']


def _memcache_country_key(location_name):
    return 'FacebookLocation.%s' % location_name

def get_country_for_location(location_name):
    memcache_key = _memcache_country_key(location_name)
    country = memcache.get(memcache_key)
    if not country:
        country = gmaps.get_geocoded_country(location_name)
        memcache.set(memcache_key, country, MEMCACHE_EXPIRY)
    return country

