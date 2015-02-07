import datetime

from google.appengine.ext import ndb

import gmaps

LOCATION_EXPIRY = 24 * 60 * 60

class CachedGeoCode(ndb.Model):
    address = property(lambda x: int(x.key().name()))
    json_data = ndb.JsonProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True, indexed=False)


def _geocode_key(**kwargs):
    return ', '.join(sorted('%s=%r' % (k, v) for (k, v) in kwargs.items()))

NO_GEOCODE = 'NO_GEOCODE'

def fetch_raw(**kwargs):
    geocode_key = _geocode_key(**kwargs)
    geocode = CachedGeoCode.get_by_id(geocode_key)
    if not geocode:
        json_data = gmaps.fetch_raw(**kwargs)
        geocode = CachedGeoCode(id=geocode_key, json_data=json_data)
        geocode.put()
    return geocode.json_data

# This should only be used by gmaps_bwcompat to populate the new cache.
def _write_cache(json_data, **kwargs):
    geocode_key = _geocode_key(**kwargs)
    geocode = CachedGeoCode.get_by_id(geocode_key)
    if not geocode:
        geocode = CachedGeoCode(id=geocode_key, json_data=json_data, date_created=datetime.datetime(2010,1,1))
        geocode.put()
    return geocode
