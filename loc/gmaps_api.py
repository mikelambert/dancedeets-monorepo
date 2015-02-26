import copy
import logging
try:
    from . import gmaps_cached
    from . import gmaps_bwcompat
    gmaps_backend = gmaps_cached
    gmaps_backend.gmaps_backend = gmaps_bwcompat
except ImportError:
    logging.error("Failed to import caching backends, defaulting to raw gmaps backend")
    from . import gmaps
    gmaps_backend = gmaps

class GeocodeException(Exception):
    pass

class GMapsGeocode(object):
    def __init__(self, json_data):
        self.json_data = json_data
        self.lookup_kwargs = {}

    def country(self, long=False):
        return self.get_component('country', long=long)

    def latlng(self):
        return (float(self.json_data['geometry']['location']['lat']), float(self.json_data['geometry']['location']['lng']))

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
        raise GeocodeException("Got unexpected status: %s" % json_result['status'])

def delete(**kwargs):
    gmaps_backend.delete(**kwargs)

def get_geocode(**kwargs):
    json_data = gmaps_backend.fetch_raw(**kwargs)
    geocode = parse_geocode(json_data)
    if geocode:
        geocode.lookup_kwargs = kwargs
    return geocode
