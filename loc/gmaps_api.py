try:
    import gmaps_cached
    gmaps_backend = gmaps_cached
except ImportError:
    import gmaps
    gmaps_backend = gmaps

class GeocodeException(Exception):
    pass

class GMapsGeocode(object):
    def __init__(self, json_data):
        self.json_data = json_data

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
        return GMapsGeocode(self.json_data)

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



def parse_geocode(json_result):
    if json_result['status'] == 'OK':
        return GMapsGeocode(json_result['results'][0])
    elif json_result['status'] == 'ZERO_RESULTS':
        return None
    else:
        raise GeocodeException("Got unexpected status: %s" % json_result['status'])

def get_geocode(**kwargs):
    json_data = gmaps_backend.fetch_raw(**kwargs)
    geocode = parse_geocode(json_data)
    return geocode
