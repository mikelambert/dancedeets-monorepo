import copy
import json
import logging

from util import runtime
from . import gmaps
from . import gmaps_prod_cache
from . import math

USE_PRIVATE_KEY = False

live_places_api = gmaps.LiveBackend('https://maps.googleapis.com', '/maps/api/place/textsearch/json', use_private_key=False)
live_geocode_api = gmaps.LiveBackend('https://maps.google.com', '/maps/api/geocode/json', use_private_key=USE_PRIVATE_KEY)

if runtime.is_local_appengine():
    remote_places_api = gmaps_prod_cache.ProdServerBackend('places', live_places_api)
    remote_geocode_api = gmaps_prod_cache.ProdServerBackend('geocode', live_places_api)
else:
    remote_places_api = live_places_api
    remote_geocode_api = live_geocode_api

try:
    from . import gmaps_cached
    places_api = gmaps_cached.CachedBackend(remote_places_api)
    # No point to checking the Cached backend on this one
    geocode_api = gmaps_cached.CachedBackend(remote_geocode_api)
except:
    logging.error("Failed to import caching backends, defaulting to raw gmaps backend")
    places_api = remote_places_api
    geocode_api = remote_geocode_api


class GeocodeException(Exception):
    def __init__(self, arg, status):
        super(GeocodeException, self).__init__(arg)
        self.status = status


class _GMapsResult(object):
    def __init__(self, json_data):
        self.json_data = json_data

    def latlng(self):
        return (float(self.json_data['geometry']['location']['lat']), float(self.json_data['geometry']['location']['lng']))

    def formatted_address(self):
        return self.json['formatted_address']

    def __repr__(self):
        return '%s(dict(%s))' % (self.__class__, json.dumps(self.__dict__, indent=2))


class GMapsGeocode(_GMapsResult):
    def __init__(self, json_data):
        self.json_data = json_data

    def country(self, long=False):
        return self.get_component('country', long=long)

    def latlng_bounds(self):
        viewport = self.json_data['geometry']['viewport']
        northeast = (viewport['northeast']['lat'], viewport['northeast']['lng'])
        southwest = (viewport['southwest']['lat'], viewport['southwest']['lng'])
        return northeast, southwest

    def copy(self):
        return GMapsGeocode(copy.deepcopy(self.json_data))

    def formatted_address(self):
        return self.json_data['formatted_address']

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


def lookup_location(location, language=None):
    if location == None:
        raise ValueError('Location cannot be None')
    logging.info('lookup location: %s', location.encode('utf-8'))
    params = {'query': location}
    if language:
        params['language'] = language
    json = places_api.get_json(**params)
    geocode = _build_geocode_from_json(json)
    if not geocode:
        params = {'address': location}
        if language:
            params['language'] = language
            json = geocode_api.get_json(**params)
            geocode = _build_geocode_from_json(json)
    return geocode

def lookup_address(address, language=None):
    if address == None:
        raise ValueError('Address cannot be None')
    logging.info('lookup address: %s', address.encode('utf-8'))
    params = {'address': address}
    if language:
        params['language'] = language
    json = geocode_api.get_json(**params)
    geocode = _build_geocode_from_json(json)
    if not geocode:
        params = {'query': address}
        if language:
            params['language'] = language
        place_json = places_api.get_json(**params)
        place_geocode = _build_geocode_from_json(place_json)
        if place_geocode:
            params = {'address': place_geocode.json_data['formatted_address']}
            if language:
                params['language'] = language
            json = geocode_api.get_json(**params)
            geocode = _build_geocode_from_json(json)
    return geocode


def _get_size(geocode):
    try:
        ne, sw = geocode.latlng_bounds()
        return math.get_distance(ne, sw)
    except:
        return None

def _choose_best_geocode(g1, g2):
    g1_size = _get_size(g1)
    g2_size = _get_size(g2)
    if g1_size is not None and g2_size is not None:
        if g1_size > g2_size:
            return g2
        else:
            return g1
    else:
        g1_size = g1.formatted_address()
        g2_size = g1.formatted_address()
        if g1_size > g2_size:
            return g2
        else:
            return g1

def _find_best_geocode(s, language=None):
    """A more versatile lookup function that uses two google apis,
    though returns unknown-type data that may or may not have viewports or address_components."""
    location_geocode = lookup_location(s, language=language)
    address_geocode = lookup_address(s, language=language)
    logging.info('location lookup: %s', location_geocode)
    logging.info('address lookup: %s', address_geocode)
    if location_geocode:
        if address_geocode:
            return _choose_best_geocode(location_geocode, address_geocode)
        else:
            return location_geocode
    else:
        if address_geocode:
            return address_geocode
        else:
            return None

def lookup_string(s, language=None):
    geocode = _find_best_geocode(s, language=language)
    if geocode:
        if 'address_components' in geocode.json_data and 'geometry' in geocode.json_data:
            return geocode
        else:
            logging.info('lookup_string result does not have address or geomtry, doing geocode address lookup on: %s', geocode.formatted_address())
            new_geocode = lookup_address(geocode.formatted_address())
            if new_geocode:
                return new_geocode
            else:
                logging.info('Faking an empty address_components for now, since at least the latlong is correct')
                geocode.json_data['address_components'] = []
                return geocode
    else:
        return None

def lookup_latlng(latlng):
    json = geocode_api.get_json(latlng='%s,%s' % latlng)
    return _build_geocode_from_json(json)


def _build_geocode_from_json(json_data):
    try:
        geocode = parse_geocode(json_data)
    except GeocodeException as e:
        if e.status == 'INVALID_REQUEST':
            return None
        raise
    return geocode


def fetch_place_as_json(query=None, language=None):
    params = {}
    params['query'] = query
    if language is not None:
        params['language'] = language

    return places_api.get_json(**params)
