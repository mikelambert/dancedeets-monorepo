import argparse
from collections import Counter
import csv
import datetime
import json
import logging
import random
import site
import StringIO
import sys

site.addsitedir('lib')

logging.basicConfig(level=logging.DEBUG)

from google.cloud import datastore
from google.cloud.datastore import query
from google.cloud.datastore import helpers

import apache_beam as beam
from apache_beam import pvalue
from apache_beam import typehints
from apache_beam.io.textio import WriteToText
from apache_beam.io.gcp.datastore.v1.datastoreio import ReadFromDatastore
from apache_beam.io.gcp.datastore.v1.datastoreio import WriteToDatastore
from apache_beam.metrics import Metrics
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

TOP_DISPLAY_CITY_N = 10
TOP_CITY_N = 100

TOP_ATTENDEE = 'TA_MARK'


def ConvertToEntity(element):
    return helpers.entity_from_protobuf(element)


def CountableEvent(db_event, ground_truth_events):
    # Don't use auto-events to train...could have a runaway AI system there!
    #TODO: Use Constants
    if ':' in db_event.key.name:
        namespace = db_event.key.name.split(':')[0]
    else:
        namespace = 'FB'
    can_use_event = not ground_truth_events or db_event['creating_method'] != 'CM_AUTO_ATTENDEE'
    if namespace == 'FB' and can_use_event:
        try:
            fb_event = json.loads(db_event['fb_event'])
            if not fb_event['empty']:
                yield db_event, fb_event
        except TypeError:
            logging.warning('Strange json data in dbevent: %s', db_event.key)


class GetEventAndAttending(beam.DoFn):
    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, (db_event, fb_event)):
        key = self.client.key('FacebookCachedObject', '701004.%s.OBJ_EVENT_ATTENDING' % db_event.key.name)
        fb_event_attending_record = self.client.get(key)
        if fb_event_attending_record:
            if 'json_data' in fb_event_attending_record:
                fb_event_attending = json.loads(fb_event_attending_record['json_data'])
                if fb_event_attending.get('empty'):
                    return
                if 'attending' in fb_event_attending:
                    yield db_event, fb_event, fb_event_attending['attending'].get('data', [])
                else:
                    logging.warning('Strange attending object: %s: %s', key, fb_event_attending)
            else:
                logging.warning('Strange attending record: %s: %s', key, fb_event_attending_record)


def ExportPeople((db_event, fb_event, attending)):
    # Count admins
    fb_info = fb_event['info']
    admins = fb_info.get('admins', {}).get('data')
    if not admins:
        if fb_info.get('owner'):
            admins = [fb_info.get('owner')]
        else:
            admins = []

    for admin in admins:
        for y in track_person('ADMIN', db_event, admin, fb_info['id']):
            yield y

    # Count attendees
    admin_hash = fb_info.get('owner', {}).get('id', random.random())

    # We don't want to use the 'maybe' lists in computing who are the go-to people for each city/style,
    # because they're not actually committed to these events.
    # Those who have committed to going should be the relevant authorities.

    for attendee in attending:
        for y in track_person('ATTENDEE', db_event, attendee, admin_hash):
            yield y


def track_person(person_type, db_event, person, count_once_per):
    '''Yields json({person-type, category, city}) to 'count_once_per: id: name' '''
    base_key = {
        'person_type': person_type,
        'city': db_event['city_name'],
        'count_once_per': count_once_per,
        'person_id': person['id'],
        'person_name': person.get('name'),
        'event_id': db_event.key.name,
    }

    key = base_key.copy()
    key['category'] = ''
    yield key

    for category in db_event.get('auto_categories', []):
        key = base_key.copy()
        key['category'] = category
        yield key


def DebugExportEventPeopleForGrouping(data):
    if data['person_type'] != 'ATTENDEE':
        return
    if data['category'] != '':
        return
    key = {
        'city': data['city'],
        'person_id': data['person_id'],
    }
    yield key, (data['count_once_per'], data['event_id'])


def DebugGroupEventIds((key, values)):
    token_to_event_ids = {}
    for value in values:
        token, event_id = value
        if token in token_to_event_ids:
            token_to_event_ids[token].append(event_id)
        else:
            token_to_event_ids[token] = [event_id]
    yield key, token_to_event_ids


def DebugExplodeAttendeeList((key, sorted_people)):
    # key contains {person_type, city, category}
    if key['person_type'] != 'ATTENDEE':
        return
    # We don't want to use category in our key...
    # And we do want to be category-less...
    # But we want to grab all potential attendees in the sub-styles as well
    # Because we will want to debug where the "Ukranian flex" scene comes from.
    #if key['category'] != '':
    #    return
    new_key = {
        'city': key['city'],
    }
    for person in sorted_people:
        final_key = new_key.copy()
        final_key['person_id'] = person['person_id']
        yield final_key, TOP_ATTENDEE


def DebugFilterForTopAttendee((key, values)):
    values = list(values)
    if TOP_ATTENDEE in values:
        new_values = [x for x in values if x != TOP_ATTENDEE]
        if len(new_values) != 1:
            logging.error('Key %s had unexpected trimmed new_values length == %s, values: %s', key, len(new_values), new_values)
        else:
            yield key, new_values[0]


class DebugBuildPRDebugAttendee(beam.DoFn):
    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, (key, grouped_events), timestamp):
        # TODO: Sync with server/logic
        key_name = '%s: %s' % (key['city'], key['person_id'])
        db_key = self.client.key('PRDebugAttendee', key_name)
        debug_attendee = datastore.Entity(key=db_key, exclude_from_indexes=['grouped_event_ids'])
        debug_attendee['created_date'] = timestamp

        debug_attendee['city'] = key['city']
        debug_attendee['person_id'] = key['person_id']
        debug_attendee['grouped_event_ids'] = json.dumps(grouped_events)
        yield debug_attendee


def GroupAttendenceByPerson(data):
    if data['person_type'] != 'ATTENDEE':
        return
    # This captures everything, unlike the subsets captured in each category
    if data['category'] != '':
        return
    # If the event doesn't have a location, don't worry about using it to infer location
    if data['category'] == 'Unknown':
        return
    yield data['person_id'], data['city']


def CountPersonTopCities((person_id, cities)):
    total_events = 0
    events_per_city = Counter()
    for city in cities:
        total_events += 1
        events_per_city[city] += 1

    min_events = 5
    min_fraction = 0.2
    # We must have at least "min_events" in one city
    # and we must have at least "min_fraction" of our events in one city
    # Without these, the cities don't count, and without cities, we don't persist this data
    min_threshold = max(min_events, total_events * min_fraction)
    top_cities = []
    for city, count in events_per_city.iteritems():
        if count > min_threshold:
            top_cities.append(city)

    # Try to limit our yielding to noteworthy people
    if top_cities:
        yield {'person_id': person_id, 'top_cities': top_cities, 'total_events': total_events}
    else:
        logging.info('%s: %s', person_id, sorted(events_per_city.items(), key=lambda x: -x[1]))


class BuildPRPersonCity(beam.DoFn):
    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, obj, timestamp):
        db_key = self.client.key('PRPersonCity', obj['person_id'])
        # TODO: db_key = person_city.key(self.client, person_id)
        person_city = datastore.Entity(key=db_key, exclude_from_indexes=['top_cities'])
        person_city['top_cities'] = obj['top_cities']
        person_city['total_events'] = obj['total_events']
        yield person_city


def ToJson(value):
    yield json.dumps(value, sort_keys=True)


def ToJsonKeys((key, value)):
    yield json.dumps(key, sort_keys=True), value


def FromJson(value):
    yield json.loads(value)


def FromJsonKeys((key, value)):
    yield (json.loads(key), value)


def GroupPeopleByCategory(data):
    #logging.debug('GroupPeopleByCategory: %r', value)
    new_key = data.copy()
    del new_key['event_id']  # Don't need
    del new_key['count_once_per']
    del new_key['person_id']
    del new_key['person_name']
    new_value = {
        'count_once_per': data['count_once_per'],
        'person_id': data['person_id'],
        'person_name': data['person_name'],
    }
    # key contains {person_type, city, category}
    yield (new_key, new_value)


def CountPeopleInfos((key, people_infos)):
    array_of_frozen_sets = (frozenset(sorted(x.items())) for x in people_infos)

    people_counts = {}
    person_lookup = {}
    for people_info_items in set(array_of_frozen_sets):
        people_info = dict(people_info_items)
        person_id = people_info['person_id']
        if person_id in people_counts:
            people_counts[person_id] += 1
        else:
            people_counts[person_id] = 1
        person_lookup[person_id] = people_info['person_name']

    # We use the person_id in there for repeat-stability when choosing the top people
    sorted_counts = sorted(people_counts.iteritems(), key=lambda (person_id, count): (-count, person_id))
    sorted_people = [{
        'person_id': pid,
        'person_name': person_lookup[pid],
        'count': count,
    } for pid, count in sorted_counts]
    # key contains {person_type, city, category}
    yield (key, sorted_people[:TOP_CITY_N])


def CityToCategoryPeople((key, people)):
    within_city_category = {
        'category': key['category'],
        'person_type': key['person_type'],
    }
    yield (key['city'], [within_city_category, people])


class BuildPRCityCategory(beam.DoFn):
    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, (key, sorted_people), timestamp, table_name, people_length):
        key_name = '%s: %s: %s' % (key['person_type'], key['city'], key['category'])
        db_key = self.client.key(table_name, key_name)
        ranking = datastore.Entity(key=db_key, exclude_from_indexes=['top_people_json'])
        ranking['created_date'] = timestamp

        ranking['person_type'] = key['person_type']
        ranking['city'] = key['city']
        ranking['category'] = key['category']
        ranking['top_people_json'] = json.dumps(sorted_people[:people_length])
        yield ranking


class WriteToDatastoreSingle(beam.DoFn):
    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, entity, actually_save=True):
        if actually_save:
            self.client.put(entity)


def ConvertDictToText(d):
    yield '%s' % json.dumps(d)


def ConvertFromEntity(entity):
    return helpers.entity_to_protobuf(entity)


def Logger(entity, prefix):
    logging.info('%s: %r', prefix, entity)
    yield entity


def run_pipeline(project, pipeline_options, run_locally, args):
    """Creates a pipeline that reads entities from Cloud Datastore."""

    ground_truth_events = args.ground_truth_events
    debug_attendees = args.debug_attendees
    want_top_attendees = args.want_top_attendees
    person_locations = args.person_locations

    p = beam.Pipeline(options=pipeline_options)
    # Create a query to read entities from datastore.
    client = datastore.Client()
    q = client.query(kind='DBEvent')

    if run_locally:
        q.key_filter(client.key('DBEvent', '999'), '>')
        q.key_filter(client.key('DBEvent', 'A'), '<')

    # Let's build a timestamp to save all our objects with
    timestamp = datetime.datetime.now()

    # Set up our map/reduce pipeline
    produce_attendees = (
        p |
        'read from datastore' >> ReadFromDatastore(project, query._pb_from_query(q), num_splits=400) |
        'convert to entity' >> beam.Map(ConvertToEntity) |
        # Find the events we want to count, and expand all the admins/attendees
        'filter events' >> beam.FlatMap(CountableEvent, ground_truth_events) |
        'load fb attending' >> beam.ParDo(GetEventAndAttending()) |
        'export attendees' >> beam.FlatMap(ExportPeople)
    ) # yapf: disable


    if want_top_attendees or debug_attendees:
        top_attendee_lists = (
            produce_attendees |
            'map category -> person' >> beam.FlatMap(GroupPeopleByCategory) |
            'group by category' >> beam.GroupByKey() |
            'build top-people lists' >> beam.FlatMap(CountPeopleInfos)
        ) # yapf: disable
    if want_top_attendees:
        (
            top_attendee_lists |
            'convert dict to json' >> beam.ParDo(ConvertDictToText) |
            'write json' >> WriteToText('gs://dancedeets-hrd.appspot.com/people-ranking-outputs/city-category/%s/data' % timestamp, file_name_suffix='.txt')
            #'generate PRCityCategory database record' >> beam.ParDo(BuildPRCityCategory(), timestamp, 'PRCityCategory', TOP_CITY_N) |
            #'write PRCityCategory to datastore (unbatched)' >> beam.ParDo(WriteToDatastoreSingle(), actually_save=not run_locally)
        ) # yapf: disable

    if person_locations:
        build_person_cities = (
            produce_attendees |
            'map attendee -> city' >> beam.FlatMap(GroupAttendenceByPerson) |
            'group by attendee' >> beam.GroupByKey() |
            'build top-cities per-person' >> beam.FlatMap(CountPersonTopCities) |
            'convert dict to json' >> beam.ParDo(ConvertDictToText) |
            'write json' >> WriteToText('gs://dancedeets-hrd.appspot.com/people-ranking-outputs/people-city/%s/data' % timestamp, file_name_suffix='.txt')
            #'build PRPersonCity' >> beam.ParDo(BuildPRPersonCity(), timestamp) |
            #'write PRPersonCity to datastore (unbatched)' >> beam.ParDo(WriteToDatastoreSingle(), actually_save=not run_locally)
        ) # yapf: disable

    if debug_attendees:
        attendee_event_debugging = (
            produce_attendees |
            'map city-attendee -> event' >> beam.FlatMap(DebugExportEventPeopleForGrouping) |
            'group by city-attendee' >> beam.GroupByKey() |
            'within city-attendee, group event_ids by admin_hash' >> beam.FlatMap(DebugGroupEventIds)
        ) # yapf: disable

        exploded_top_attendees = (
            top_attendee_lists |
            'explode the top attendees into a mapping: category-attendee -> YES' >> beam.FlatMap(DebugExplodeAttendeeList)
            # We don't deal with duplicates, since it requires the objects (ie our dicts) to be hashable
            # Instead, we rely on DebugFilterForTopAttendee to filter out duplicates created by the above
            # | 'remove duplicates from multiple overlapping attendee-lists' >> beam.RemoveDuplicates()
        ) # yapf: disable

        (
            # These both have the same keys:
            # key contains {person_type, city, category, person_id}
            (attendee_event_debugging, exploded_top_attendees) | beam.Flatten() |
            # keys are {city, person_id}
            'group the attendee-debug info with the is-it-a-top-attendee info' >> beam.GroupByKey() |
            'filter for TOP_ATTENDEE' >> beam.FlatMap(DebugFilterForTopAttendee) |
            'build PRDebugAttendee' >> beam.ParDo(DebugBuildPRDebugAttendee(), timestamp) |
            'write PRDebugAttendee to datastore (unbatched)' >> beam.ParDo(WriteToDatastoreSingle(), actually_save=not run_locally)
        ) # yapf: disable
    """
    (output
        | 'convert from entity' >> beam.Map(ConvertFromEntity)
        | 'write to datastore' >> WriteToDatastore(client.project)
    )
    """

    # Actually run the pipeline (all operations above are deferred).
    result = p.run()
    # Wait until completion, main thread would access post-completion job results.
    result.wait_until_finish()
    return result


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run_locally', dest='run_locally', default='', help='Run data subset and do not save.')
    parser.add_argument('--debug_attendees', dest='debug_attendees', default=False, type=bool, help='Generate PRDebugAttendee data')
    parser.add_argument('--want_top_attendees', dest='want_top_attendees', default=False, type=bool, help='Generate PRCityCategory data')
    parser.add_argument('--person_locations', dest='person_locations', default=False, type=bool, help='Generate PRPersonCity data')
    parser.add_argument(
        '--ground_truth_events',
        dest='ground_truth_events',
        default=False,
        type=bool,
        help='Only use real-events, not events added as a result of this pipeline data'
    )
    known_args, pipeline_args = parser.parse_known_args()
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    gcloud_options = pipeline_options.view_as(GoogleCloudOptions)
    run_pipeline('dancedeets-hrd', gcloud_options, known_args.run_locally, known_args)


if __name__ == '__main__':
    run()
