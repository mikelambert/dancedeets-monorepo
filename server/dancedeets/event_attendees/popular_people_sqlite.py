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
from dancedeets.util import sqlite_db
from dancedeets.util import timelog


class FakePRCityCategory(object):
    pass


def get_people_rankings_for_city_names_sqlite(city_names, attendees_only):
    conn = sqlite_db.get_connection('pr_city_category')
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
