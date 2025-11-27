#!/usr/bin/python

from __future__ import absolute_import

import getpass
import json
import logging
import re
import sqlite3
import requests

from dancedeets import facebook
from dancedeets.util import urls

from dancedeets.geonames import geoname_files
from dancedeets.geonames import sqlite_db

FILENAME_ADLOCS = '/Users/%s/Dropbox/dancedeets-development/server/generated/adlocs_only.db' % getpass.getuser()

FACEBOOK_CONFIG = None


def get_config():
    global FACEBOOK_CONFIG
    if not FACEBOOK_CONFIG:
        FACEBOOK_CONFIG = facebook.load_yaml('facebook-dev.yaml')
    return FACEBOOK_CONFIG


def number(x):
    return re.match(r'^\d+$', x)


def get_query(geoname):
    city_state_list = [
        geoname.ascii_name,  # city name
        geoname.admin1_code,  # state name
    ]
    city_state = ', '.join(x for x in city_state_list if x and not number(x))
    return city_state


def load_targeting_key(cursor, geoname):
    geo_search = {
        'location_types': 'city,region',
        'country_code': geoname.country_code,
        'q': get_query(geoname),
        'type': 'adgeolocation',
        'access_token': get_config()['app_access_token'],
        'locale': 'en_US',  # because app_access_token is locale-less and seems to use a IP-locale fallback
    }
    cursor.execute('select data from AdGeoLocation where q = ? and country_code = ?', (geo_search['q'], geo_search['country_code']))
    result = cursor.fetchone()
    if not result:
        response = requests.get('https://graph.facebook.com/v2.9/search', params=geo_search)
        result_json = response.json()
        array_json = json.dumps(result_json['data'])
        data = {
            'q': geo_search['q'],
            'country_code': geo_search['country_code'],
            'data': array_json,
        }
        sqlite_db.insert_record(cursor, 'AdGeoLocation', data)
        print('\n'.join('- ' + str(x) for x in result_json['data']))


def fetch_database():
    conn = sqlite3.connect(FILENAME_ADLOCS)
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS AdGeoLocation
        (q text, country_code text, data text,
        PRIMARY KEY (q, country_code))
    '''
    )

    for geoname in geoname_files.cities(5000):
        load_targeting_key(cursor, geoname)
    conn.commit()


if __name__ == '__main__':
    fetch_database()
