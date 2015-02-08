from __future__ import absolute_import
import math
import logging

rad = math.pi / 180.0

def expand_bounds(latlng_bounds, distance_in_km):
    northeast, southwest = latlng_bounds

    logging.info("1 NE %s, SW %s", northeast, southwest)

    offsets_northeast = _get_lat_lng_offsets(northeast, distance_in_km)
    offsets_southwest = _get_lat_lng_offsets(southwest, distance_in_km)

    def add_latlngs(x, y):
        return (x[0] + y[0], x[1] + y[1])
    def sub_latlngs(x, y):
        return (x[0] - y[0], x[1] - y[1])
    northeast = add_latlngs(northeast, offsets_northeast)
    southwest = sub_latlngs(southwest, offsets_southwest)

    logging.info("2 NE %s, SW %s", northeast, southwest)

    return southwest, northeast # ordered more negative to more positive

def get_distance(latlng1, latlng2, use_km=False):
    dlat = (latlng2[0]-latlng1[0]) * rad
    dlng = (latlng2[1]-latlng1[1]) * rad
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
        math.cos(latlng1[0] * rad) * math.cos(latlng2[0] * rad) * 
        math.sin(dlng/2) * math.sin(dlng/2))
    circum = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))
    if use_km:
        radius = 6371 # km
    else:
        radius = 3959 # miles
    distance = radius * circum
    return distance

# UNUSED!
def _contains(bounds, latlng):
    lats_good = bounds[0][0] < latlng[0] < bounds[1][0]
    if bounds[0][1] < bounds[1][1]:
        lngs_good = bounds[0][1] < latlng[1] < bounds[1][1]
    else:
        lngs_good = bounds[0][1] < latlng[1] or latlng[1] < bounds[1][1]
    return lats_good and lngs_good

def _get_lat_lng_offsets(latlng, km):
    miles = km_in_miles(km)
    miles_per_nautical_mile = 1.15078
    lat_range = miles / (miles_per_nautical_mile * 60.0)
    lng_range = miles / (math.cos(latlng[0] * rad) * miles_per_nautical_mile * 60.0)
    return lat_range, lng_range

def miles_in_km(miles):
    return miles * 1.609344
def km_in_miles(km):
    return km * 0.6213712
