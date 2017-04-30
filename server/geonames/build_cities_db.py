#!/usr/bin/python

from __future__ import absolute_import

import json
import re
import sqlite3
import urllib

import facebook
from util import urls
from geonames import geoname_files
from geonames import sqlite_db
from geonames import fetch_adgeolocs

def number(x):
    return re.match(r'^\d+$', x)

FILENAME_CITIES = '/Users/lambert/Dropbox/dancedeets/data/generated/cities.db'

conn_adlocs = sqlite3.connect(fetch_adgeolocs.FILENAME_ADLOCS)
cursor_adlocs = conn_adlocs.cursor()

conn_cities = sqlite3.connect(FILENAME_CITIES)
cursor_cities = conn_cities.cursor()
cursor_cities.execute('''DROP TABLE IF EXISTS City''')
cursor_cities.execute('''CREATE TABLE City
             (geoname_id integer primary key, ascii_name text, admin1_code text, country_code text, latitude real, longitude real, population integer, timezone text, adgeolocation_key)''')

def get_fb_targeting_key(geoname):
    q = fetch_adgeolocs.get_query(geoname)
    country_code = geoname.country_code
    db_result = cursor_adlocs.execute('SELECT data from AdGeoLocation where q = ? and country_code = ?', (q, country_code)).fetchone()
    results = json.loads(db_result[0])
    if results:
        return results[0]['key']
    else:
        return None


for geoname in geoname_files.cities(5000):
    adgeolocation_key = get_fb_targeting_key(geoname)

    if not geoname.population:
        print geoname.geoname_id, geoname.ascii_name, geoname.population
    data = {
        'geoname_id': geoname.geoname_id,
        'ascii_name': geoname.ascii_name,
        'admin1_code': geoname.admin1_code,
        'country_code': geoname.country_code,
        'latitude': geoname.latitude,
        'longitude': geoname.longitude,
        'population': geoname.population or 0,
        'timezone': geoname.timezone,
        'adgeolocation_key': adgeolocation_key,
    }
    sqlite_db.insert_record(cursor_cities, 'City', data)

conn_cities.commit()
conn_adlocs.commit()
