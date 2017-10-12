from collections import Counter
from google.cloud import datastore
"""
PersonCity
- id: person_id
- total: integer (total event count)
- geoname_ids: [integer]
  # these are the cities this user is in
  # all cities?
  # major cities?
  # just the cities with >X% ?
"""

client = None


def generate_client():
    global client
    client = datastore.Client('dancedeets-hrd')


generate_client()


def key(client, person_id):
    return client.key('PRPersonCity', person_id, exclude_from_indexes=['top_cities'])


def get_multi_geoname_ids(person_ids):
    keys = [key(client, person_id) for person_id in person_ids]
    person_cities = client.get_multi(keys)
    return [x['top_cities'] if x else [] for x in person_cities]


def create(person_id, top_cities, total_events):
    task = datastore.Entity(key=key(client, person_id))
    task.update({'top_cities': top_cities, 'total_events': total_events})
    client.put(task)


def get_sorted_locations(person_ids):
    geoname_ids_list = get_multi_geoname_ids(person_ids)
    counts = Counter()
    for top_cities in geoname_ids_list:
        for id in top_cities:
            counts[id] += 1
    return sorted(counts, lambda x: -counts[x])
