#!/usr/bin/python
#
# import PR data into sqlite
import commands
import json
import getpass
import os
import site
import sqlite3

site.addsitedir('lib-local')

from dancedeets.geonames import sqlite_db

DB_PATH = '/Users/%s/Dropbox/dancedeets-development/server/generated/' % getpass.getuser()


def _get_path():
    path = os.path.join(os.path.dirname(__file__), 'tmp')
    return path


def download_files():
    path = _get_path()
    try:
        os.makedirs(path)
    except OSError:
        pass
    #for filename in os.listdir(path):
    #    print 'deleting', filename
    #    os.remove(os.path.join(path, filename))

    print 'Downloading CSV files'
    command = 'gsutil -m rsync -R -C -d gs://dancedeets-hrd.appspot.com/people-ranking-outputs/ %s/people-ranking-outputs/' % path
    commands.getoutput(command)


def iterate_most_recent(job_name):
    job_path = get_most_recent(job_name)
    for filename in os.listdir(job_path):
        print 'Importing file %s' % filename
        for row in open(os.path.join(job_path, filename)):
            yield json.loads(row.strip())


def get_most_recent(job_name):
    path = _get_path()
    job_path = os.path.join(path, 'people-ranking-outputs', job_name)
    timestamps = sorted(os.listdir(job_path), key=lambda x: x)
    full_path = os.path.join(job_path, timestamps[-1])
    return full_path


def save_personcity_db(clear=True):
    conn = sqlite3.connect(os.path.join(DB_PATH, 'pr_person_city.db'))
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

    for data in iterate_most_recent('people-city'):
        data['top_cities'] = json.dumps(data['top_cities'])
        sqlite_db.insert_record(cursor, 'PRPersonCity', data)

    conn.commit()


def save_citycategory_db(clear=True):
    conn = sqlite3.connect(os.path.join(DB_PATH, 'pr_city_category.db'))
    cursor = conn.cursor()
    if clear:
        cursor.execute('''DROP TABLE IF EXISTS PRCityCategory''')
        cursor.execute(
            '''
            CREATE TABLE PRCityCategory
            (
            person_type text not null,
            geoname_id text not null,
            category text not null,
            top_people_json text,
            PRIMARY KEY (person_type, geoname_id, category)
            )
            '''
        )
        cursor.execute('''
            CREATE INDEX no_person_type ON PRCityCategory
            (geoname_id, category)
            ''')
    for data, top_people_json in iterate_most_recent('city-category'):
        data['top_people_json'] = json.dumps(top_people_json)
        sqlite_db.insert_record(cursor, 'PRCityCategory', data)

    conn.commit()


if __name__ == '__main__':
    download_files()
    save_personcity_db()
    save_citycategory_db()
