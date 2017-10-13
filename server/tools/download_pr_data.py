#!/usr/bin/python
#
# import PR data into sqlite
import commands
import json
import getpass
import os
import site
import sqlite3
import StringIO
import sys

site.addsitedir('lib-local')

from google.cloud import storage
from google.cloud import datastore
from dancedeets.geonames import sqlite_db

FULL_CITY_CATEGORY_DB = '/Users/%s/Dropbox/dancedeets-development/server/generated/pr_city_category_full.db' % getpass.getuser()
TRIMMED_CITY_CATEGORY_DB = '/Users/%s/Dropbox/dancedeets-development/server/generated/pr_city_category.db' % getpass.getuser()

PERSON_CITY_DB = '/Users/%s/Dropbox/dancedeets-development/server/generated/pr_person_city.db' % getpass.getuser()


def save_personcity_db(clear=True):
    conn = sqlite3.connect(PERSON_CITY_DB)
    cursor = conn.cursor()
    if clear:
        cursor.execute('''DROP TABLE IF EXISTS PRPersonCity''')
        cursor.execute(
            '''
            CREATE TABLE PRPersonCity
            (
            person_id text not null,
            top_cities text,
            total_events integer not null,
            PRIMARY KEY (person_id)
            )
            '''
        )

    path = os.path.join(os.path.dirname(__file__), 'test')
    try:
        os.makedirs(path)
    except OSError:
        pass
    for filename in os.listdir(path):
        print 'deleting', filename
        os.remove(os.path.join(path, filename))

    print 'Downloading CSV files'
    commands.getoutput('gsutil -m cp gs://dancedeets-hrd.appspot.com/test/* %s' % path)
    for filename in os.listdir(path):
        print 'Loading blob %s' % filename
        for row in open(os.path.join(path, filename)):
            data = json.loads(row.strip())
            data['top_cities'] = json.dumps(data['top_cities'])
            sqlite_db.insert_record(cursor, 'PRPersonCity', data)

    conn.commit()


def save_citycategory_db(clear=False):
    conn = sqlite3.connect(FULL_CITY_CATEGORY_DB)
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


def copy_citycategory_db(clear=True):
    old_conn = sqlite3.connect(FULL_CITY_CATEGORY_DB)
    old_cursor = old_conn.cursor()
    new_conn = sqlite3.connect(TRIMMED_CITY_CATEGORY_DB)
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
        print TRIMMED_CITY_CATEGORY_DB
    else:
        save_personcity_db()
        # Rewrite these as 'download files'
        # save_citycategory_db()
        # copy_citycategory_db()
