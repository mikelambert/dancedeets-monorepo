#!/usr/bin/python

import sys
sys.path += ['..']
import geohash

cities = []

for line in open(sys.argv[1]):
    # List of fields from http://download.geonames.org/export/dump/
    geonameid, name, asciiname, alternatenames, latitude, longitude, feature_class, feature_code, country_code, cc2, admin1_code, admin2_code, admin3_code, admin4_code, population, elevation, gtopo30, timezone, modification_date = line.split('\t')
    
    if int(population) < 100000:
        continue
    city_geohash = str(geohash.Geostring((float(latitude), float(longitude)), depth=10))
    cities.append((city_geohash, timezone, asciiname+" "+admin2_code))

cities.sort()
for city in cities:
    print '\t'.join(city)

