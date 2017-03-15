import json
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
    top_people_json = ndb.JsonProperty()
    # top_people_json is [['id: name', count], ...]

    @property
    def human_category(self):
        # '' represents 'Overall'
        return event_types.CATEGORY_LOOKUP.get(self.category, '')

STYLES_SET = set(x.index_name for x in event_types.STYLES)

def get_people_rankings_for_city_names(city_names, attendees_only=False):
    if runtime.is_local_appengine() and False:
        people_rankings = load_from_dev(city_names, attendees_only=attendees_only)
    else:
        args = []
        if attendees_only:
            args = [PeopleRanking.person_type=='ATTENDEE']
        people_rankings = PeopleRanking.query(
            PeopleRanking.city.IN(city_names),
            *args
        )
    return people_rankings

def load_from_dev(city_names, attendees_only):
    from google.cloud import datastore

    rankings = []
    client = datastore.Client()

    for city_name in city_names:
        q = client.query(kind='PeopleRanking')
        q.add_filter('city', '=', city_name)
        if attendees_only:
            q.add_filter('person_type', '=', 'ATTENDEE')

        for result in q.fetch(100):
            ranking = PeopleRanking()
            ranking.person_type = result['person_type']
            ranking.city = result['city']
            ranking.category = result['category']
            ranking.top_people_json = result['top_people_json']
            rankings.append(ranking)
    return rankings

def get_city_names_near(latlong):
    if latlong == (None, None):
        return []
    southwest, northeast = math.expand_bounds((latlong, latlong), 100)
    logging.info('Looking up nearby cities to %s', latlong)
    included_cities = cities.get_nearby_cities((southwest, northeast), only_populated=True)
    logging.info('Found %s cities', len(included_cities))
    biggest_cities = sorted(included_cities, key=lambda x: -x.population)[:10]
    city_names = [city.display_name() for city in biggest_cities]
    return city_names

def get_attendees_near(latlong):
    city_names = get_city_names_near(latlong)
    logging.info('Loading PeopleRanking for top 10 cities: %s', city_names)
    if not city_names:
        return {}
    try:
        people_rankings = get_people_rankings_for_city_names(city_names, attendees_only=True)
        logging.info('Loaded People Rankings')
        groupings = combine_rankings(people_rankings)
    except:
        logging.exception('Error creating combined people rankings')
        return {}
    return groupings.get('ATTENDEE', {})

def combine_rankings(rankings):
    groupings = {}
    for r in rankings:
        #logging.info(r.key)
        key = (r.person_type, r.human_category)
        # Make sure we use setdefault....we can have key repeats due to rankings from different cities
        groupings.setdefault(key, {})
        # Use this version below, and avoid the lookups
        people = groupings[key]
        if r.top_people_json:
            for person_name, count in r.top_people_json:
                if person_name in people:
                    people[person_name] += count
                else:
                    people[person_name] = count
        else:
            # bwcompat
            for person_triplet in r.top_people:
                person_name, new_count = person_triplet.rsplit(':', 1)
                if person_name in people:
                    people[person_name] += int(new_count)
                else:
                    people[person_name] = int(new_count)
    for key in groupings:
        person_type, category = key
        if person_type == 'ATTENDEE':
            limit = 3
        elif person_type == 'ADMIN':
            limit = 2
        else:
            logging.error('Unknown person type: %s', person_type)
        # Remove low/bad frequency data
        groupings[key] = dict(kv for kv in groupings[key].iteritems() if kv[1] >= limit)

    groupings = dict(kv for kv in groupings.iteritems() if len(kv[1]))

    final_groupings = {}
    for key in groupings:
        person_type, category = key
        orig = groupings[key]
        dicts = []
        for name, count in orig.iteritems():
            split_name = name.split(': ', 1)
            dicts.append({
                'id': split_name[0],
                'name': split_name[1],
                'count': count,
            })
        if person_type not in final_groupings:
            final_groupings[person_type] = {}
        if category not in final_groupings[person_type]:
            final_groupings[person_type][category] = {}
        final_groupings[person_type][category] = sorted(dicts, key=lambda x: -x['count'])
    return final_groupings


def encode_map_result(key, value):
    return json.dumps(key, sort_keys=True).encode('utf-8'), value.encode('utf-8')

def track_person(person_type, db_event, person, count_once_per=None):
    if count_once_per is None:
        # This is a nice way to ensure each id counts once per...id
        # (ie, every id counts)
        count_once_per = person['id']
    """Yields json({person-type, category, city}) to 'count_once_per: id: name' """
    person_name = '%s: %s: %s' % (count_once_per, person['id'], person.get('name'))
    # Not using db_event.nearby_city_names since it's way too slow.
    # And we just search-many-cities on lookup time.
    for city in [db_event.city_name]:
        key = {
            'person_type': person_type,
            'category': '',
            'city': city,
        }
        yield encode_map_result(key, person_name)
        for category in STYLES_SET.intersection(db_event.auto_categories):
            key = {
                'person_type': person_type,
                'category': category,
                'city': city,
            }
            yield encode_map_result(key, person_name)

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
        admin_hash = ','.join(sorted([x['id'] for x in db_event.admins]))
        # We don't want to use the 'maybe' lists in computing who are the go-to people for each city/style,
        # because they're not actually committed to these events.
        # Those who have committed to going should be the relevant authorities.
        for attendee in fb_event_attending['attending']['data']:
            for y in track_person('ATTENDEE', db_event, attendee, admin_hash):
                yield y

def reduce_popular_people(key, people_json):
    """Takes json({person-type, category, city}), ['count_once_per: id: name', ...]"""
    bucket = json.loads(key)

    counts = {}
    for full_person_name in people_json:
        count_once_per, person_name = full_person_name.split(': ', 1)
        if person_name in counts:
            counts[person_name].add(count_once_per)
        else:
            counts[person_name] = set([count_once_per])
    count_list = [(person_json, len(unique_organizers)) for (person_json, unique_organizers) in counts.items()]
    # count_list is [['id: name', count_of_unique_organizers], ...]
    sorted_counts = sorted(count_list, key=lambda kv: -kv[1])

    # Yes, key is the same as type_city_category above.
    # But we're declaring our key explicitly, here.
    key = '%s: %s: %s' % (bucket['person_type'], bucket['city'], bucket['category'])
    ranking = PeopleRanking.get_or_insert(key)
    ranking.person_type = bucket['person_type']
    ranking.city = bucket['city']
    ranking.category = bucket['category']
    ranking.top_people_json = sorted_counts[:TOP_N]
    # TODO: delete
    # Clean this field out
    # ranking.top_people = []

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
