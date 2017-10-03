#!/usr/bin/python
#
# import google cloud datastore into sqlite

import getpass
import sqlite3

from google.cloud import datastore
from dancedeets.geonames import sqlite_db

FILENAME_DB = '/Users/%s/Dropbox/dancedeets-development/server/generated/pr_city_category.db' % getpass.getuser()


def all_rows():
    return []


def save_db(clear=False):
    conn = sqlite3.connect(FILENAME_DB)
    cursor = conn.cursor()
    if clear:
        cursor.execute('''DROP TABLE IF EXISTS PRCityCategory''')
        cursor.execute('''
            )''')
    client = datastore.Client()
    query = client.query(kind='PRCityCategory')
    query.order = ['person_type', 'city', 'category']
    query.add_filter('person_type', '=', 'ATTENDEE')
    for data in query.fetch():
        print data['person_type'], data['city'], data['category']
        sqlite_db.insert_record(cursor, 'PRCityCategory', data)

    conn.commit()


if __name__ == '__main__':
    save_db(clear=False)
