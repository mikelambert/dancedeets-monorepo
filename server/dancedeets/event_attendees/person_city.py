from collections import Counter
import json

from dancedeets.util import sqlite_db


def get_top_city_for(person_ids):
    conn = sqlite_db.get_connection('pr_person_city')
    cursor = conn.cursor()

    query = 'SELECT top_cities from PRPersonCity where person_id in (%s)' % ','.join('?' * len(person_ids))
    params = list(person_ids)
    cursor.execute(query, params)

    counts = Counter()
    for result in cursor.fetchall():
        top_cities = json.loads(result[0])
        for id in top_cities:
            counts[id] += 1
    top_city = sorted(counts, key=lambda x: -counts[x])[0]
    return top_city
