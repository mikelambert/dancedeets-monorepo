from __future__ import absolute_import
import math

import geohash

from loc import math as loc_math

circumference_of_earth = 40000.0 # km
def get_geohash_bits_for_km(km):
    if km < min_box_size:
        return max_geohash_bits
    geohash_bits = int(math.ceil(-math.log(1.0 * km / circumference_of_earth) / math.log(2)))
    return geohash_bits

def get_km_for_geohash_bits(precision):
    km = circumference_of_earth * math.pow(2, -precision)
    return km

min_box_size = 200 # km
max_geohash_bits = get_geohash_bits_for_km(min_box_size)
# max_geohash_bits should be 8, which is reasonable compared to 32 possible for complete geohashing


def get_all_geohashes_for(bounds, precision=None):
    if not precision:
        # We subtract one in an attempt to get less geohashes below (by using a larger search area),
        # but be aware we still risk having at most 5 geohashes in a worst-case edge-border
        # 90miles in NY = 2 geohashes
        # 90miles in SF = 3 geohashes
        km = loc_math.get_distance(bounds[0], bounds[1], use_km=True)
        precision = get_geohash_bits_for_km(km) - 1

    center = (
        (bounds[0][0] + bounds[1][0]) / 2,
        (bounds[0][1] + bounds[1][1]) / 2
    )

    # to understand why this is necessary, see the BACKGROUND of:
    # https://github.com/davetroy/geohash-js/blob/master/README
    pinpoints = [
        center,
        bounds[0],
        bounds[1],
        (bounds[0][0], bounds[1][1]),
        (bounds[1][0], bounds[0][1]),
    ]
    geohashes = set()
    for point in pinpoints:
        geohashes.add(str(geohash.Geostring(point, depth=precision)))
    return list(geohashes)
