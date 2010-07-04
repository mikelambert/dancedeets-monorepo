import sys

# import time
# import re
# for d in open('events/cities.txt').read().split('\n'):
#   f = repr((d,locations._raw_get_geocoded_location(d)['latlng']))
#   f = re.sub(re.sub('9999*[0-9]', '', f), '0000*[0-9]', '')
#   f = re.sub('0000*[0-9]', '', re.sub('9999*[0-9]', '', f))
#   print f
#   time.sleep(1)

IMPORTANT_CITIES = [
    ('New York City', (40.7142691, -74.0059729)),
    ('Southern California', (33.6839473, -117.7946942)),
    ('Northern California', (37.7749294, -122.4194155)),
    ('Chicago, Illinois', (41.850033, -87.6500522)),
    ('Seattle, Washington', (47.6062094, -122.3320708)),
    ('Boston, Massachusetts', (42.3584308, -71.0597731)),
    ('Las Vegas, Nevada', (36.114646, -115.172816)),
    ('Houston, Texas', (29.7628844, -95.3830614)),
    ('Washington, District of Columbia', (38.8951118, -77.0363657)),
    ('Atlanta, Georgia', (33.7489953, -84.3879823)),
    ('Honolulu, Hawaii', (21.3069443, -157.8583333)),
]

extra = [
    ('Phoenix, Arizona', (33.4483771, -112.0740373)),
    ('Philadelphia, Pennsylvania', (39.952334, -75.163788)),
    ('San Antonio, Texas', (29.424122, -98.493628)),
    ('San Diego, California', (32.7153291, -117.1572551)),
    ('Dallas, Texas', (32.802954, -96.769923)),
    ('San Jose, California', (37.3393857, -121.8949554)),
    ('Detroit, Michigan', (42.331426, -83.0457538)),
    ('Jacksonville, Florida', (30.3321837, -81.655651)),
    ('Indianapolis, Indiana', (39.7683765, -86.1580423)),
    ('Austin, Texas', (30.267153, -97.7430607)),
    ('Columbus, Ohio', (39.9611755, -82.9987942)),
    ('Fort Worth, Texas', (32.725408, -97.3208496)),
    ('Charlotte, North Carolina', (35.2270869, -80.8431266)),
    ('Memphis, Tennessee', (35.1495342, -90.0489800)),
    ('Baltimore, Maryland', (39.2903847, -76.6121892)),
    ('El Paso, Texas', (31.7587198, -106.4869314)),
    ('Seattle, Washington', (47.6062094, -122.3320708)),
    ('Denver, Colorado', (39.7391536, -104.9847034)),
    ('Nashville, Tennessee', (36.1658899, -86.7844431)),
    ('Milwaukee, Wisconsin', (43.0389024, -87.9064735)),
    ('Louisville, Kentucky', (38.2542376, -85.759406)),
    ('Portland, Oregon', (45.5234515, -122.6762071)),
    ('Oklahoma City, Oklahoma', (35.4675602, -97.5164276)),
    ('Tucson, Arizona', (32.2217429, -110.926479)),
    ('Albuquerque, New Mexico', (35.0844908, -106.6511367)),
    ('Kansas, City Missouri', (39.0997265, -94.5785666)),
    ('Fresno, California', (36.7477272, -119.7723661)),
    ('Sacramento, California', (38.5815719, -121.4943995)),
    ('Omaha, Nebraska', (41.254005, -95.57)),
    ('Virginia Beach, Virginia', (36.8529263, -75.977985)),
    ('Miami, Florida', (25.7742657, -80.1936589)),
    ('Cleveland, Ohio', (41.4994954, -81.6954087)),
    ('Raleigh, North Carolina', (35.772095, -78.6386145)),
    ('Colorado Springs, Colorado', (38.8338815, -104.8213634)),
    ('Tulsa, Oklahoma', (36.1539816, -95.992774)),
    ('Minneapolis, Minnesota', (44.9799653, -93.2638361)),
    ('St Louis, Missouri', (38.646991, -90.224967)),
    ('New Orleans, Louisiana', (29.9647222, -90.0705556)),
    ('Cincinnati, Ohio', (39.1361111, -84.5030555)),
    ('Newark, New Jersey', (40.735657, -74.1723666)),
    ('Irvine, California', (33.6839473, -117.7946942)),
    ('San Bernadino, California', (34.1083448, -117.2897652)),
]

def get_nearest_city(latitude, longitude):
    closest_city = None
    closest_distance_squared = sys.maxint
    for city_name, latlng in IMPORTANT_CITIES:
        latdiff = (latlng[0] - latitude)
        lngdiff = (latlng[1] - longitude)
        distance_squared = latdiff*latdiff + lngdiff*lngdiff
        if distance_squared < closest_distance_squared:
            closest_city = city_name
            closest_distance_squared = distance_squared
    return closest_city


def sort_by_closest(latitude, longitude):
    def distance(x):
        city_name, (city_latitude, city_longitude) = x
        latdiff = city_latitude - latitude
        lngdiff = city_longitude - longitude
        distance_squared = latdiff*latdiff + lngdiff*lngdiff
        return distance_squared
    return [x[0] for x in sorted(IMPORTANT_CITIES, key=distance)]
