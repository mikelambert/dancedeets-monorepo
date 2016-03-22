import copy
import logging

from . import gmaps

USE_PRIVATE_KEY = False

live_places_api = gmaps.LiveBackend('https://maps.googleapis.com', '/maps/api/place/textsearch/json', use_private_key=False)
live_geocode_api = gmaps.LiveBackend('https://maps.google.com', '/maps/api/geocode/json', use_private_key=USE_PRIVATE_KEY)

try:
    from . import gmaps_cached
    from . import gmaps_bwcompat
    places_api = gmaps_cached.CachedBackend(live_places_api)
    # No point to checking the Cached backend on this one
    geocode_api = gmaps_bwcompat.BwCachedBackend(gmaps_cached.CachedBackend(live_geocode_api))
except:
    logging.error("Failed to import caching backends, defaulting to raw gmaps backend")
    places_api = live_places_api
    geocode_api = live_geocode_api


class GeocodeException(Exception):
    def __init__(self, arg, status):
        super(GeocodeException, self).__init__(arg)
        self.status = status


class _GMapsResult(object):
    def __init__(self, json_data):
        self.json_data = json_data
        self.lookup_kwargs = {}

    def latlng(self):
        return (float(self.json_data['geometry']['location']['lat']), float(self.json_data['geometry']['location']['lng']))

    def formatted_address(self):
        return self.json['formatted_address']


class GMapsGeocode(_GMapsResult):
    def __init__(self, json_data):
        self.json_data = json_data
        self.lookup_kwargs = {}

    def country(self, long=False):
        return self.get_component('country', long=long)

    def latlng_bounds(self):
        viewport = self.json_data['geometry']['viewport']
        northeast = (viewport['northeast']['lat'], viewport['northeast']['lng'])
        southwest = (viewport['southwest']['lat'], viewport['southwest']['lng'])
        return northeast, southwest

    def copy(self):
        return GMapsGeocode(copy.deepcopy(self.json_data))

    def address_components(self):
        return self.json_data['address_components']

    def get_component(self, name, long=True):
        components = [x[long and 'long_name' or 'short_name'] for x in self.json_data['address_components'] if name in x['types']]
        if components:
            return components[0]
        else:
            return None

    # This function seems very wrong and dangerous, and we should fix up the API not to need it
    def delete_component(self, name):
        self.json_data['address_components'] = [x for x in self.json_data['address_components'] if name not in x['types']]


def GMapsPlace(_GMapsResult):
    pass


def convert_geocode_to_json(geocode):
    if geocode:
        return {'status': 'OK', 'results': [geocode.json_data]}
    else:
        return {'status': 'ZERO_RESULTS'}


def parse_geocode(json_result):
    if json_result['status'] == 'OK':
        return GMapsGeocode(json_result['results'][0])
    elif json_result['status'] == 'ZERO_RESULTS':
        return None
    else:
        raise GeocodeException("Got unexpected status: %s" % json_result['status'], json_result['status'])


def delete(**kwargs):
    # Use the geocode api since it's the more complete one that lets us delete from more backends.
    geocode_api.delete(**kwargs)


def get_geocode(**kwargs):
    json_data = _fetch_geocode_as_json(**kwargs)
    try:
        geocode = parse_geocode(json_data)
    except GeocodeException as e:
        if e.status == 'INVALID_REQUEST':
            return None
        raise
    if geocode:
        geocode.lookup_kwargs = kwargs
    return geocode


def _fetch_geocode_as_json(address=None, latlng=None, language=None, region=None, components=None):
    params = {}
    if address is not None:
        params['address'] = address
    if latlng is not None:
        params['latlng'] = '%s,%s' % latlng
    assert params
    if language is not None:
        params['language'] = language
    if region is not None:
        params['region'] = region
    if components is not None:
        params['components'] = components

    return geocode_api.get_json(**params)


def fetch_place_as_json(query=None, language=None):
    params = {}
    params['query'] = query
    if language is not None:
        params['language'] = language

    return places_api.get_json(**params)
