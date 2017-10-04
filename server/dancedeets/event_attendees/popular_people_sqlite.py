from atomicwrites import atomic_write
import sqlite3
import getpass
import json
import logging
import threading
import time
import os

from google.cloud import storage

from dancedeets.util import runtime
from dancedeets.util import timelog

DEV_DB = '/Users/%s/Dropbox/dancedeets-development/server/generated/pr_city_category.db' % getpass.getuser()
SERVER_DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pr_city_category.db')

FILE_COPY_LOCK = threading.Lock()


def download_sqlite():
    logging.info('Grabbing file-copy lock')
    if FILE_COPY_LOCK.acquire():
        # Check it again, now that we've finally gotten the lock
        logging.info('Grabbed lock, checking if file exists: %s', os.path.exists(SERVER_DB))
        if not os.path.exists(SERVER_DB):
            # TODO: ensure we copy to a staging ground, and move it into place (so no one tries to open a malformed file)
            client = storage.Client('dancedeets-hrd')
            bucket = client.get_bucket('dancedeets-dependencies')
            logging.info('Downloading file')
            blob = bucket.get_blob('pr_city_category.db')
            # Luckily this only takes around 5-10 seconds (for street dance) when run on GCE instances
            contents = blob.download_as_string()
            with atomic_write(SERVER_DB, overwrite=True) as f:
                f.write(contents)
                # SERVER_DB doesn't exist yet.
            # Now it does.
        FILE_COPY_LOCK.release()


def _get_connection():
    if runtime.is_local_appengine():
        filename_db = DEV_DB
    else:
        filename_db = SERVER_DB
        if not os.path.exists(filename_db):
            start = time.time()
            download_sqlite()
            timelog.log_time_since('Downloading PRCityCategory sqlite db', start)
    conn = sqlite3.connect(filename_db)
    # Cannot be shared between threads, be careful if making this global!
    return conn


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
