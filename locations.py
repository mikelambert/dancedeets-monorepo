import logging
from loc import gmaps_api
from loc import math as loc_math

# http://en.wikipedia.org/wiki/Mile
MILES_COUNTRIES = ['UK', 'US']

LOCATION_EXPIRY = 24 * 60 * 60

def get_location_bounds(address, distance_in_km):
    if not address:
        return None, None
    geocode = gmaps_api.get_geocode(address=address)
    if not geocode:
        return None, None
    northeast, southwest = geocode.latlng_bounds()

    logging.info("1 NE %s, SW %s", northeast, southwest)

    offsets_northeast = loc_math.get_lat_lng_offsets(northeast, distance_in_km)
    offsets_southwest = loc_math.get_lat_lng_offsets(southwest, distance_in_km)

    def add_latlngs(x, y):
        return (x[0] + y[0], x[1] + y[1])
    def sub_latlngs(x, y):
        return (x[0] - y[0], x[1] - y[1])
    northeast = add_latlngs(northeast, offsets_northeast)
    southwest = sub_latlngs(southwest, offsets_southwest)

    logging.info("2 NE %s, SW %s", northeast, southwest)

    return southwest, northeast # ordered more negative to more positive

def get_getgeocoded_name(geocode):
    if not geocode:
        return None
    return _get_name(geocode.json_data)

def get_name(**kwargs):
    geocode = gmaps_api.get_geocode(**kwargs)
    return get_getgeocoded_name(geocode)

def get_name_and_latlng(**kwargs):
    geocode = gmaps_api.get_geocode(**kwargs)
    if not geocode:
        return None
    latlng = geocode.latlng()
    return _get_name(geocode.json_data), latlng

def get_latlng(**kwargs):
    geocode = gmaps_api.get_geocode(**kwargs)
    if not geocode:
        return None
    return geocode.latlng()

def get_country_for_location(long_name=False, **kwargs):
    geocode = gmaps_api.get_geocode(**kwargs)
    return geocode.country(long=long_name)

def _get_name(result):
    def get(name, long=True):
        components = [x[long and 'long_name' or 'short_name'] for x in result['address_components'] if name in x['types']]
        # Sometimes we see this, so return both 
        #{
        #  "long_name" : "Naka Ward",
        #  "short_name" : "Naka Ward",
        #  "types" : [ "locality", "political" ]
        #},
        #{
        #  "long_name" : "Nagoya",
        #  "short_name" : "Nagoya",
        #  "types" : [ "locality", "political" ]
        #},
        return components
        
    city_parts = []
    # TODO(lambert): Things to test and verify:
    # Bay Area, San Francisco, Brooklyn, New York, Tokyo, Osaka/Shibuya, Europe/Asia, The Haight
    city_parts.extend(get('locality') or get('sublocality') or get('administrative_area_level_3') or get('administrative_area_level_2') or get('colloquial_area'))
    country = get('country')
    if country:
        if country == ['United States']:
            city_parts.extend(get('administrative_area_level_1', long=False))
            city_parts.extend(get('country', long=False))
        else:
            city_parts.extend(get('administrative_area_level_1', long=False))
            city_parts.extend(country)
    else:
        if get('continent'):
            city_parts.extend(get('continent'))
        else:
            city_parts.extend(get('natural_feature'))

    city_name = ', '.join(x for x in city_parts if x)

    if not city_name:
        logging.warning("Could not get city for geocode results: %s", result)
    return city_name


