#!/usr/bin/python
#
# import google cloud datastore into sqlite

import getpass
import sqlite3
import sys

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
        cursor.execute(
            '''
            CREATE TABLE PRCityCategory
            (
            created_date text not null,
            person_type text not null,
            city text not null,
            category text not null,
            top_people_json text,
            PRIMARY KEY (person_type, city, category)
            )
            '''
        )
        cursor.execute('''
            CREATE INDEX no_person_type ON PRCityCategory
            (city, category)
            ''')
    client = datastore.Client()
    query = client.query(kind='PRCityCategory')
    query.order = ['person_type', 'city', 'category']
    query.add_filter('person_type', '=', 'ATTENDEE')
    for data in query.fetch():
        print data['person_type'], data['city'], data['category']
        sqlite_db.insert_record(cursor, 'PRCityCategory', data)

    conn.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'db_name':
        print FILENAME_DB
    else:
        save_db(clear=False)
