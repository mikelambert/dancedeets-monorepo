import sqlite3
import getpass
import json
import os

from google.cloud import storage

from dancedeets.util import runtime
from dancedeets.util import timelog

DEV_DB = '/Users/%s/Dropbox/dancedeets-development/server/generated/pr_city_category.db' % getpass.getuser()
SERVER_DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pr_city_category.db')


def download_sqlite():
    client = storage.Client()
    bucket = client.get_bucket('dancedeets-dependencies')
    blob = bucket.get_blob('pr_city_category.db')
    # Luckily this only takes around 5-10 seconds (for street dance) when run on GCE instances
    contents = blob.download_as_string()
    open(SERVER_DB, 'w').write(contents)


CONN = None


def _get_connection():
    global CONN
    if CONN:
        return CONN
    if runtime.is_local_appengine():
        filename_db = DEV_DB
    else:
        filename_db = SERVER_DB
        if not os.path.exists(filename_db):
            start = time.time()
            download_sqlite()
            timelog.log_time_since('Downloading PRCityCategory sqlite db', start)
    CONN = sqlite3.connect(filename_db)
    return CONN


class FakePRCityCategory(object):
    pass


def get_people_rankings_for_city_names_sqlite(city_names, attendees_only):
    conn = _get_connection()
    cursor = conn.cursor()

    query = 'SELECT person_type, city, category, top_people_json from PRCityCategory where city in (%s)' % ','.join('?' * len(city_names))
    params = list(city_names)
    if attendees_only:
        query += '  AND person_type = ?'
        params += ['ATTENDEE']

    cursor.execute(query, params)
    rankings = []
    for result in cursor.fetchall():
        ranking = FakePRCityCategory()
        # ranking.key = ndb.Key('PRCityCategory', result.)
        ranking.person_type = result[0]
        ranking.city = result[1]
        ranking.category = result[2]
        ranking.top_people_json = json.loads(result[3])
        rankings.append(ranking)
    return rankings
