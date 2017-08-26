#!/usr/bin/python

from __future__ import absolute_import

import json
import os
import re
import sqlite3
import sys
import urllib

from util import urls
from geonames import geoname_files
from geonames import sqlite_db
from geonames import fetch_adgeolocs


def get_fb_targeting_key(cursor_adlocs, geoname):
    q = fetch_adgeolocs.get_query(geoname)
    country_code = geoname.country_code
    db_result = cursor_adlocs.execute('SELECT data from AdGeoLocation where q = ? and country_code = ?', (q, country_code)).fetchone()
    results = json.loads(db_result[0])
    if results:
        return results[0]['key'], results[0]['type']
    else:
        return None, None


def save_cities_db(cities_db_filename, dummy_file=False):

    conn_cities = sqlite3.connect(cities_db_filename)
    cursor_cities = conn_cities.cursor()
    cursor_cities.execute('''DROP TABLE IF EXISTS City''')
    cursor_cities.execute(
        '''CREATE TABLE City
                 (geoname_id integer primary key, ascii_name text, admin1_code text, country_code text, latitude real, longitude real, population integer, timezone text, adgeolocation_key integer, adgeolocation_type text)'''
    )
    # We index on longitude first, since it's likely to have the greatest variability and pull in the least amount of cities
    cursor_cities.execute('''CREATE INDEX country_geo on City (country_code, longitude, latitude);''')
    cursor_cities.execute('''CREATE INDEX geo on City (longitude, latitude);''')
    if not dummy_file:
        conn_adlocs = sqlite3.connect(fetch_adgeolocs.FILENAME_ADLOCS)
        cursor_adlocs = conn_adlocs.cursor()
        for geoname in geoname_files.cities(5000):
            adgeolocation_key, adgeolocation_type = get_fb_targeting_key(cursor_adlocs, geoname)

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
                'adgeolocation_type': adgeolocation_type,
            }
            sqlite_db.insert_record(cursor_cities, 'City', data)

    conn_cities.commit()


if __name__ == '__main__':
    save_cities_db(sys.argv[1], os.environ.get('DUMMY_FILE'))
