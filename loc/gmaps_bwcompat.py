from google.appengine.ext import db

import json
from loc import gmaps_backends

LOCATION_EXPIRY = 24 * 60 * 60


class GeoCode(db.Model):
    address = property(lambda x: int(x.key().name()))
    json_data = db.TextProperty()


class BwCachedBackend(gmaps_backends.GMapsBackend):
    def __init__(self, backend):
        self.backend = backend

    @staticmethod
    def _geocode_key(address, latlng):
        assert address or latlng
        assert not (address and latlng)
        if latlng:
            latlng = '(%s, %s)' % latlng.split(',')
        if address:
            byte_length = len(repr(address))
            if byte_length > 450:
                return address[:(len(address) * 450 / byte_length)]
            else:
                return address
        else:
            return '%s,%s' % latlng

    def get_json(self, **kwargs):
        extra_keys = set(kwargs.keys()).difference(['address', 'latlng'])
        if not extra_keys:
            address = kwargs.get('address')
            latlng = kwargs.get('latlng')
            if not address and not latlng:
                return {
                    "results": [],
                    "status": "ZERO_RESULTS"
                }

            # We changed this to be clearer and more consistent, but all our geocaches use "US" as a suffix, not "United States"
            if address and address.endswith('United States'):
                address = address.replace('United States', 'US')
            geocode_key = self._geocode_key(address, latlng)
            geocode = GeoCode.get_by_key_name(geocode_key)
            if geocode:
                try:
                    geocoded_data = json.loads(geocode.json_data)
                    if not geocoded_data:
                        return {
                            "results": [],
                            "status": "ZERO_RESULTS"
                        }
                    else:
                        return {
                            "results": [geocoded_data],
                            "status": "OK"
                        }
                except:
                    pass
        return self.backend.get_json(**kwargs)
