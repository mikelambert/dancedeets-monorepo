#!/usr/bin/python
#
# import google cloud datastore into sqlite

import json
import getpass
import sqlite3
import sys

from google.cloud import datastore
from dancedeets.geonames import sqlite_db

FULL_DB = '/Users/%s/Dropbox/dancedeets-development/server/generated/pr_city_category_full.db' % getpass.getuser()
TRIMMED_DB = '/Users/%s/Dropbox/dancedeets-development/server/generated/pr_city_category.db' % getpass.getuser()


def all_rows():
    return []


def save_db(clear=False):
    conn = sqlite3.connect(FULL_DB)
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
    for data in query.fetch():
        print data['person_type'], data['city'], data['category']
        sqlite_db.insert_record(cursor, 'PRCityCategory', data)

    conn.commit()


def copy_db(clear=True):
    old_conn = sqlite3.connect(FULL_DB)
    old_cursor = old_conn.cursor()
    new_conn = sqlite3.connect(TRIMMED_DB)
    new_cursor = new_conn.cursor()
    if clear:
        new_cursor.execute('''DROP TABLE IF EXISTS PRCityCategory''')
        new_cursor.execute(
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
        new_cursor.execute('''
            CREATE INDEX no_person_type ON PRCityCategory
            (city, category)
            ''')
    old_cursor.execute('SELECT created_date, person_type, city, category, top_people_json FROM PRCityCategory')
    for data_row in old_cursor.fetchall():
        data = dict(created_date=data_row[0], person_type=data_row[1], city=data_row[2], category=data_row[3], top_people_json=data_row[4])
        print data['person_type'], data['city'], data['category']
        data['top_people_json'] = json.dumps(json.loads(data['top_people_json'])[:100])
        sqlite_db.insert_record(new_cursor, 'PRCityCategory', data)

    new_conn.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'db_name':
        print TRIMMED_DB
    else:
        save_db()
        copy_db()
