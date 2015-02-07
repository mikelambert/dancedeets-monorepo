from google.appengine.ext import db

import json
import gmaps
import logging
import smemcache

from loc import gmaps_cached

LOCATION_EXPIRY = 24 * 60 * 60

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

NO_GEOCODE = 'NO_GEOCODE'

def fetch_raw(address=None, latlng=None):
    if not address and not latlng:
        return {
            "results" : [],
            "status" : "ZERO_RESULTS"
        }
    geocode_key = _geocode_key(address, latlng)
    memcache_key = _memcache_location_key(geocode_key)
    geocoded_data = None
    if smemcache:
        geocoded_data = smemcache.get(memcache_key)
    if geocoded_data == NO_GEOCODE:
        geocoded_data = None # so we return None
    elif geocoded_data is None:
        geocode = GeoCode.get_by_key_name(geocode_key)
        data_is_good = False
        if geocode:
            data_is_good = True
            try:
                geocoded_data = json.loads(geocode.json_data)
            except:
                logging.exception("Error decoding json data for geocode %r with latlng %s: %r", address, latlng, geocode.json_data)
                data_is_good = False
        if not data_is_good:
            gmaps_geocode = gmaps.parse_geocode(gmaps.fetch_raw(address=address, latlng=latlng))
            if gmaps_geocode is not None:
                geocoded_data = gmaps_geocode.json_data
            else:
                geocoded_data = None
            geocode = GeoCode(key_name=geocode_key)
            geocode.json_data = json.dumps(geocoded_data)
            geocode.put()
        if smemcache:
            geocoded_data_for_memcache = geocoded_data
            if geocoded_data_for_memcache is None:
                geocoded_data_for_memcache = NO_GEOCODE
            smemcache.set(memcache_key, geocoded_data_for_memcache, LOCATION_EXPIRY)
    if geocoded_data is None:
        result = {
            "results" : [],
            "status" : "ZERO_RESULTS"
        }
    else:
        result = {
            "results" : [geocoded_data],
            "status" : "OK"
        }
    if result:
        kwargs = {}
        if address is not None:
            kwargs['address'] = address
        if latlng is not None:
            kwargs['latlng'] = latlng
        gmaps_cached._write_cache(result, **kwargs)
        return result
