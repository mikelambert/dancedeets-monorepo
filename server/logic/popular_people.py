import logging
import random
import re

from google.appengine.ext import ndb
from mapreduce import mapreduce_pipeline
from mapreduce import operation

import app
import base_servlet
import event_types
from events import eventdata
from loc import math
from rankings import cities
import fb_api
from util import fb_mapreduce
from util import runtime

TOP_N = 100

class PeopleRanking(ndb.Model):
    person_type = ndb.StringProperty()
    city = ndb.StringProperty()
    category = ndb.StringProperty()
    top_people = ndb.StringProperty(repeated=True, indexed=False)

    @property
    def human_category(self):
        # '' represents 'Overall'
        return event_types.CATEGORY_LOOKUP.get(self.category, '')

STYLES_SET = set(x.index_name for x in event_types.STYLES)

def faked_people_rankings():
    people_rankings = []
    for person_type in ['ADMIN', 'ATTENDEE']:
        for style in [''] + [x.index_name for x in event_types.STYLES]:
            top_people = []
            for i in range(10):
                id = random.randint(0, 100)
                top_people.append('%s: User First LastName %s: %s' % (id, id* 10000, random.randint(5, 100)))
            people_rankings.append(PeopleRanking(
                    person_type=person_type,
                    category=style,
                    top_people=top_people,
            ))
    return people_rankings

def load_from_dev(city_names):
    from google.cloud import datastore

    rankings = []
    client = datastore.Client()

    for city_name in city_names:
        q = client.query(kind='PeopleRanking')
        q.add_filter('city', '=', city_name)
        q.add_filter('person_type', '=', 'ATTENDEE')

        for result in q.fetch(100):
            ranking = PeopleRanking()
            ranking.person_type = result['person_type']
            ranking.city = result['city']
            ranking.category = result['category']
            ranking.top_people = result['top_people']
            rankings.append(ranking)
    return rankings

def get_attendee_ids_near(location_info):
    latlong = location_info.latlong()
    if latlong == (None, None):
        return []
    southwest, northeast = math.expand_bounds((latlong, latlong), 100)
    included_cities = cities.get_nearby_cities((southwest, northeast))
    biggest_cities = sorted(included_cities, key=lambda x: -x.population)[:10]
    city_names = [city.display_name() for city in biggest_cities]
    logging.info('City names: %s', city_names)
    if not city_names:
        return []
    try:
        if runtime.is_local_appengine():
            people_rankings = load_from_dev(city_names)
        else:
            people_rankings = PeopleRanking.query(
                PeopleRanking.city.IN(city_names),
                PeopleRanking.person_type=='ATTENDEE'
            )
        groupings = combine_rankings(people_rankings)
    except:
        logging.exception('Error creating combined people rankings')
        return []
    attendees = groupings.get('ATTENDEE', {}).get('', [])
    logging.info('Attendees Nearby:\n%s', '\n'.join(repr(x) for x in attendees))
    return [x['id'] for x in attendees]

def combine_rankings(rankings):
    groupings = {}
    for r in rankings:
        #logging.info(r.key)
        for person_triplet in r.top_people:
            #logging.info('  - %s', person_triplet)
            match = re.match(r'(.*): (\d+)', person_triplet)
            if not match:
                logging.error('Error parsing %s, person: %s', r.id, person_triplet)
                continue
            name, new_count = match.groups()
            groupings.setdefault(r.person_type, {}).setdefault(r.human_category, {})
            if name in groupings[r.person_type][r.human_category]:
                groupings[r.person_type][r.human_category][name] += int(new_count)
            else:
                groupings[r.person_type][r.human_category][name] = int(new_count)
    for person_type in groupings.keys():
        if person_type == 'ATTENDEE':
            limit = 3
        elif person_type == 'ADMIN':
            limit = 2
        else:
            logging.error('Unknown person type: %s', person_type)
        for category in groupings[person_type].keys():
            # Remove low/bad frequency data
            for name in groupings[person_type][category].keys():
                if groupings[person_type][category][name] < limit:
                    del groupings[person_type][category][name]
            if len(groupings[person_type][category]) == 0:
                del groupings[person_type][category]
        if len(groupings[person_type]) == 0:
            del groupings[person_type]

    for person_type in groupings:
        for category in groupings[person_type]:
            orig = groupings[person_type][category]
            dicts = [
                {
                    'name': name.split(': ', 1)[1],
                    'id': name.split(': ', 1)[0],
                    'count': count,
                } for (name, count) in orig.items()
            ]
            groupings[person_type][category] = sorted(dicts, key=lambda x: -x['count'])
    return groupings


def track_person(person_type, db_event, person):
    person_name = '%s: %s' % (person['id'], person.get('name'))
    person_name = person_name.encode('utf-8')
    # Not using db_event.nearby_city_names since it's way too slow.
    for city in [db_event.city_name]:
        key = '%s: %s: %s' % (person_type, '', city)
        yield (key.encode('utf-8'), person_name)
        for category in STYLES_SET.intersection(db_event.auto_categories):
            key = '%s: %s: %s' % (person_type, category, city)
            yield (key.encode('utf-8'), person_name)

BATCH_SIZE = 20
def output_people(db_events):
    # Don't use auto-events to train...could have a runaway AI system there!
    db_events = [x for x in db_events if x.is_fb_event and x.has_content() and x.creating_method != eventdata.CM_AUTO_ATTENDEE]

    fbl = fb_mapreduce.get_fblookup()
    fbl.request_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in db_events])
    fbl.batch_fetch()

    for db_event in db_events:
        try:
            fb_event_attending = fbl.fetched_data(fb_api.LookupEventAttending, db_event.id)
        except fb_api.NoFetchedDataException:
            logging.warning('No attending found for %s', db_event.id)
            continue
        if fb_event_attending['empty']:
            continue

        for admin in db_event.admins:
            for y in track_person('ADMIN', db_event, admin):
                yield y
        for attendee in fb_event_attending['attending']['data']:
            for y in track_person('ATTENDEE', db_event, attendee):
                yield y

def reduce_popular_people(type_city_category, people):
    person_type, category, city = type_city_category.split(': ', 2)
    counts = {}
    for person in people:
        if person in counts:
            counts[person] += 1
        else:
            counts[person] = 1
    sorted_counts = sorted(counts.items(), key=lambda kv: -kv[1])

    # Yes, key is the same as type_city_category above.
    # But we're declaring our key explicitly, here.
    key = '%s: %s: %s' % (person_type, city, category)
    ranking = PeopleRanking.get_or_insert(key)
    ranking.person_type = person_type
    ranking.city = city
    ranking.category = category
    ranking.top_people = ['%s: %s' % kv for kv in sorted_counts[:TOP_N]]
    yield operation.db.Put(ranking)

def mr_popular_people_per_city(fbl, queue):
    mapper_params = {
        'entity_kind': 'events.eventdata.DBEvent',
        'handle_batch_size': BATCH_SIZE,
    }
    mapper_params.update(fb_mapreduce.get_fblookup_params(fbl, randomize_tokens=True))
    mrp = mapreduce_pipeline.MapreducePipeline(
        'popular_people',
        'logic.popular_people.output_people',
        'logic.popular_people.reduce_popular_people',
        'mapreduce.input_readers.DatastoreInputReader',
        'mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        mapper_params=mapper_params,
        reducer_params={
            'output_writer': {
                'mime_type': 'text/plain',
                'bucket_name': 'dancedeets-hrd.appspot.com',
            },
        },
        shards=8,
    )
    mrp.start(queue_name=queue)
    return mrp

@app.route('/tools/popular_people')
class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        queue = self.request.get('queue', 'slow-queue')
        mr_popular_people_per_city(self.fbl, queue)
