import logging
import math
import sys
import locations

# import time
# import re
# for d in open('events/cities.txt').read().split('\n'):
#   f = repr((d,locations._raw_get_geocoded_location(d)['latlng']))
#   f = re.sub(re.sub('9999*[0-9]', '', f), '0000*[0-9]', '')
#   f = re.sub('0000*[0-9]', '', re.sub('9999*[0-9]', '', f))
#   print f
#   time.sleep(1)

IMPORTANT_CITIES = [
    # Down the west coast
    ('Seattle, Washington', (47.6062094, -122.3320708)),
    ('Portland, Oregon', (45.5234515, -122.6762071)),
    ('Northern California', (37.7749294, -122.4194155)),
    ('Las Vegas, Nevada', (36.114646, -115.172816)),
    ('Southern California', (33.6839473, -117.7946942)),

    # Across southern america
    ('Phoenix, Arizona', (33.4483771, -112.0740373)),
    ('Albuquerque, New Mexico', (35.0844908, -106.6511367)),
    ('El Paso, Texas', (31.7587198, -106.4869314)),
    ('San Antonio, Texas', (29.424122, -98.493628)),
    ('Dallas, Texas', (32.802954, -96.769923)),
    ('Houston, Texas', (30.240086,-95.932617)),
    ('New Orleans, Louisiana', (29.9647222, -90.0705556)),
    ('Memphis, Tennessee', (35.1495342, -90.0489800)),
    ('Nashville, Tennessee', (36.1658899, -86.7844431)),
    # Across northern america
    ('Minneapolis, Minnesota', (44.9799653, -93.2638361)),
    ('Chicago, Illinois', (41.850033, -87.6500522)),
    ('Detroit, Michigan', (42.331426, -83.0457538)),
    ('Buffalo, New York', (42.332662, -83.045654)),
    ('Syracuse, New York', (43.048141, -76.147446)),
    # Across middle america
    ('Denver, Colorado', (39.7391536, -104.9847034)),
    ('Oklahoma City, Oklahoma', (35.4675602, -97.5164276)),
    ('Omaha, Nebraska', (41.254005, -95.57)),
    ('Kansas City, Kansas', (39.0997265, -94.5785666)),
    ('St Louis, Missouri', (38.646991, -90.224967)),
    ('Louisville, Kentucky', (38.2542376, -85.759406)),
    # Down the east coast
    ('Boston, Massachusetts', (42.3584308, -71.0597731)),
    ('New York City', (40.7142691, -74.0059729)),
    ('Washington, District of Columbia', (38.8951118, -77.0363657)),
    ('Virginia Beach, Virginia', (36.8529263, -75.977985)),
    ('Charlotte, North Carolina', (35.2270869, -80.8431266)),
    ('Atlanta, Georgia', (33.7489953, -84.3879823)),
    ('Jacksonville, Florida', (30.3321837, -81.655651)),
    ('Miami, Florida', (25.7742657, -80.1936589)),
    # Other
    ('Honolulu, Hawaii', (21.3069443, -157.8583333)),

]

def get_closest_city(latitude, longitude):
    city_distance = lambda city: locations.get_distance(latitude, longitude, city[1][0], city[1][1])
    closest_city = min(IMPORTANT_CITIES, key=city_distance)
    return closest_city[0]

def get_cities_within(latitude, longitude, distance_in_km):
    radius = 6371
    deg_per_rad = 57.2957795
    if distance_in_km < radius:
        bigger_angle_rad = math.asin(1.0 * distance_in_km / radius)
    else:
        bigger_angle_rad = 1.0
    bigger_angle_deg = bigger_angle_rad * deg_per_rad
    candidate_cities = [(city_name, latlng) for (city_name, latlng) in IMPORTANT_CITIES
            if abs(latlng[0]-latitude) < bigger_angle_deg and abs(latlng[1]-longitude) < bigger_angle_deg]
    within_cities = [city_name for (city_name, latlng) in candidate_cities
            if locations.get_distance(latitude, longitude, latlng[0], latlng[1], use_km=True) < distance_in_km]
    logging.info("Went from %s important cities to %s candidate cities to %s actual cities within %s km", len(IMPORTANT_CITIES), len(candidate_cities), len(within_cities), distance_in_km)
    return within_cities
