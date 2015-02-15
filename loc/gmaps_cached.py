import logging

from google.appengine.ext import ndb

import gmaps
gmaps_backend = gmaps

LOCATION_EXPIRY = 24 * 60 * 60

class CachedGeoCode(ndb.Model):
    address = property(lambda x: int(x.key().name()))
    json_data = ndb.JsonProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True, indexed=False)


def _geocode_key(**kwargs):
    if not kwargs:
        raise ValueError("Cannot pass empty parameters to gmaps fetch function! kwargs=%r", kwargs)
    return ', '.join(sorted('%s=%r' % (k, unicode(v).strip().lower()) for (k, v) in kwargs.items()))

NO_GEOCODE = 'NO_GEOCODE'

def fetch_raw(**kwargs):
    geocode_key = _geocode_key(**kwargs)
    geocode = CachedGeoCode.get_by_id(geocode_key)
    if geocode:
        json_data = geocode.json_data
    else:
        json_data = gmaps_backend.fetch_raw(**kwargs)
        if json_data['status'] in ['OK', 'ZERO_RESULTS']:
            geocode = CachedGeoCode(id=geocode_key, json_data=json_data)
            geocode.put()
    return json_data

def cleanup_bad_data(geocode):
    logging.info("%s: %s", geocode.key, geocode.json_data['status'])
    if geocode.json_data['status'] not in ['OK', 'ZERO_RESULTS']:
        geocode.key.delete()
