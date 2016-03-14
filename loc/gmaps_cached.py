import logging

from google.appengine.ext import ndb

from . import gmaps
from . import gmaps_backends

LOCATION_EXPIRY = 24 * 60 * 60


class CachedGeoCode(ndb.Model):
    address = property(lambda x: int(x.key().name()))
    json_data = ndb.JsonProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True, indexed=False)


class CachedBackend(gmaps_backends.GMapsBackend):
    def __init__(self, backend):
        self.backend = backend

    @staticmethod
    def _geocode_key(**kwargs):
        if not kwargs:
            raise ValueError("Cannot pass empty parameters to gmaps fetch function! kwargs=%r", kwargs)
        new_kwargs = kwargs.copy()
        if 'latlng' in new_kwargs:
            new_kwargs['latlng'] = '(%s, %s)' % new_kwargs['latlng'].split(',')
        for k, v in new_kwargs.items():
            byte_length = len(repr(v))
            if byte_length > 400:
                new_kwargs[k] = v[:(len(v) * 400 / byte_length)]
        return ', '.join(sorted('%s=%r' % (k, unicode(v).strip().lower()) for (k, v) in new_kwargs.items()))

    def get_json(self, **kwargs):
        geocode_key = self._geocode_key(**kwargs)
        geocode = CachedGeoCode.get_by_id(geocode_key)
        if geocode:
            json_data = geocode.json_data
        else:
            json_data = self.backend.get_json(**kwargs)
            if json_data['status'] in ['OK', 'ZERO_RESULTS']:
                geocode = CachedGeoCode(id=geocode_key, json_data=json_data)
                geocode.put()
        return json_data

    def delete(self, **kwargs):
        geocode_key = self._geocode_key(**kwargs)
        ndb.Key(CachedGeoCode, geocode_key).delete()
        self.backend.delete(**kwargs)
