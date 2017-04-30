#!/usr/bin/python

from __future__ import absolute_import

import json
import logging
import re
import sqlite3
import urllib

import facebook
from util import urls
from geonames import geoname_files
from geonames import sqlite_db

FILENAME_CITIES = 'rankings/cities_only.db'
FILENAME_ADLOCS = 'rankings/adlocs_only.db'

def number(x):
    return re.match(r'^\d+$', x)


conn_adlocs = sqlite3.connect(FILENAME_ADLOCS)
cursor_adlocs = conn_adlocs.cursor()
cursor_adlocs.execute('''CREATE TABLE IF NOT EXISTS AdGeoLocation
             (q text, country_code text, data text)''')

conn_cities = sqlite3.connect(FILENAME_CITIES)
cursor_cities = conn_cities.cursor()
cursor_cities.execute('''DROP TABLE City''')
cursor_cities.execute('''CREATE TABLE City
             (geonameid integer primary key, city_name text, state_name text, country_name text, latitude real, longitude real, population integer, timezone text)''')

for geoname in geoname_files.cities(5000):
    data = {
        'geoname_id': geoname_id,
        'city_name': asciiname,
        'state_name': admin1_code,
        'country_name': country_code,
        'latitude': float(latitude),
        'longitude': float(longitude),
        'population': int(population),
        'timezone': timezone,
    }


    key = get_fb_targeting_key(data)

    sqlite_db.insert_record(cursor_cities, 'City', data)
conn_cities.commit()
conn_adlocs.commit()
