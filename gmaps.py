import math
import urllib
import urllib2

# facebook.py deals with google-appengine wrapping, so use theirs
import facebook
simplejson = facebook.simplejson
urlread = facebook.urlread

def get_geocoded_data(address):
    url = "http://maps.google.com/maps/api/geocode/json?address=%s&sensor=false" % urllib.quote_plus(address)
    json_result = simplejson.load(urllib.urlopen(url))
    # TODO(lambert): return as Exceptions
    assert json_result['status'] == 'OK'
    result = json_result['results'][0]
    return result

def get_geocoded_address(address):
    result = get_geocoded_data(address)
    geocoded_location = {}
    geocoded_location['lat'] = result['geometry']['location']['lat']
    geocoded_location['lng'] = result['geometry']['location']['lng']
    geocoded_location['address'] = result['formatted_address']
    return geocoded_location

def get_geocoded_country(address):
    result = get_geocoded_data(address)
    geocoded_location = {}
    countries = [x['short_name'] for x in result['address_components'] if u'country' in x['types']]
    #TODO(lambert): handle with exceptions
    assert len(countries) == 1
    return countries[0]

def get_distance(lat1, lng1, lat2, lng2, use_km=False):
    deg_to_rad = 57.2957795
    dlat = (lat2-lat1) / deg_to_rad
    dlng = (lng2-lng1) / deg_to_rad
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
        math.cos(lat1 / deg_to_rad) * math.cos(lat2 / deg_to_rad) * 
        math.sin(dlng/2) * math.sin(dlng/2))
    circum = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
    if use_km:
        radius = 3959 # miles
    else:
        radius = 6371 # km
    distance = radius * circum
    return distance

