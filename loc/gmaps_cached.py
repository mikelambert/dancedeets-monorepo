from google.appengine.ext import ndb

import gmaps

LOCATION_EXPIRY = 24 * 60 * 60

class CachedGeoCode(ndb.Model):
    address = property(lambda x: int(x.key().name()))
    json_data = ndb.JsonProperty()


def _geocode_key(**kwargs):
    return ', '.join(sorted('%r=%r' % (k, v) for (k, v) in kwargs.items()))

NO_GEOCODE = 'NO_GEOCODE'

def _raw_get_cached_geocoded_data(address=None, latlng=None, language=None):
    if not address and not latlng:
        return {}
    geocode_key = _geocode_key(address, latlng, language)
    geocode = CachedGeoCode.get_by_id(geocode_key)
    if not geocode:
        json_data = gmaps.fetch_raw(address=address, latlng=latlng, language=language)
        geocode = CachedGeoCode(id=geocode_key, json_data=json_data)
        geocode.put()
    return geocode.json_data
