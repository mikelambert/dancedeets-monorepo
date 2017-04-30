#!/usr/bin/python

from __future__ import absolute_import

import json
import logging
import re
import sqlite3
import urllib

import facebook
from util import urls


FILENAME_CITIES = 'rankings/cities_only.db'
FILENAME_ADLOCS = 'rankings/adlocs_only.db'

FACEBOOK_CONFIG = facebook.load_yaml('facebook-dev.yaml')

def number(x):
    return re.match(r'^\d+$', x)

def get_fb_targeting_key(data):
    city_state_list = [
        data['city_name'],
        data['state_name'],
    ]
    city_state = ', '.join(x for x in city_state_list if x and not number(x))
    print city_state, data['country_name']
    geo_search = {
        'location_types': 'city,region',
        'country_code': data['country_name'],
        'q': city_state,
        'type': 'adgeolocation',
        'access_token': FACEBOOK_CONFIG['app_access_token'],
        'locale': 'en_US', # because app_access_token is locale-less and seems to use a IP-locale fallback
    }
    cursor_adlocs.execute('select data from AdGeoLocation where q = ? and country_code = ?', (geo_search['q'], geo_search['country_code']))
    result = cursor_adlocs.fetchone()
    if not result:
        result = urllib.urlopen('https://graph.facebook.com/v2.9/search?%s' % urls.urlencode(geo_search)).read()
        result_json = json.loads(result)
        array_json = json.dumps(result_json['data'])
        data = {
            'geonameid': data['geonameid'],
            'q': geo_search['q'],
            'country_code': geo_search['country_code'],
            'data': array_json,
        }
        insert_record(cursor_adlocs, 'AdGeoLocation', data)
        print '\n'.join('- ' + str(x) for x in result_json['data'])

def insert_record(cursor, table_name, data):
    key_values = data.items()

    insert_sql = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table_name,
        ', '.join(kv[0] for kv in key_values),
        ', '.join('?' for kv in key_values),
    )
    try:
        result = cursor.execute(insert_sql, [kv[1] for kv in key_values])
    except Exception as e:
        logging.exception('Found problems with data: %s', data)
    cursor.connection.commit()

conn_adlocs = sqlite3.connect(FILENAME_ADLOCS)
cursor_adlocs = conn_adlocs.cursor()
cursor_adlocs.execute('''CREATE TABLE IF NOT EXISTS AdGeoLocation
             (q text, country_code text, data text)''')

conn_cities = sqlite3.connect(FILENAME_CITIES)
cursor_cities = conn_cities.cursor()
cursor_cities.execute('''DROP TABLE City''')
cursor_cities.execute('''CREATE TABLE City
             (geonameid integer primary key, city_name text, state_name text, country_name text, latitude real, longitude real, population integer, timezone text)''')

count = 0
for line in open('/Users/lambert/Dropbox/dancedeets/data/cities5000.txt'):
    count += 1
    line = line.decode('utf-8')

    if not count % 1000:
        logging.info('Imported %s cities', count)
    # List of fields from http://download.geonames.org/export/dump/
    geonameid, name, asciiname, alternatenames, latitude, longitude, feature_class, feature_code, country_code, cc2, admin1_code, admin2_code, admin3_code, admin4_code, population, elevation, gtopo30, timezone, modification_date = line.split('\t')

    #if int(population) < 50000:
    #    print name, population
    #    continue

    data = {
        'geonameid': geonameid,
        'city_name': asciiname,
        'state_name': admin1_code,
        'country_name': country_code,
        'latitude': float(latitude),
        'longitude': float(longitude),
        'population': int(population),
        'timezone': timezone,
    }


    key = get_fb_targeting_key(data)

    insert_record(cursor_cities, 'City', data)
conn_cities.commit()
conn_adlocs.commit()
