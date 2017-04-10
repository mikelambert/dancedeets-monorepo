import datetime
import json
import logging
import random
import site
import sys

"""
pip install 'git+https://github.com/apache/beam.git#egg=0.7.0-dev&subdirectory=sdks/python' -t lib
pip install googledatastore google-apitools -t lib
pip install google-cloud-datastore --user (cant use lib/)

python -m popular_people --log=DEBUG

OR FOR SERVER RUNS:

wget https://github.com/apache/beam/archive/master.zip
unzip master.zip
cd beam-master/sdks/python/
python setup.py sdist
cd ../../..
export SDK=beam-master/sdks/python/dist/apache-beam-0.7.0.dev0.tar.gz
export BUCKET=gs://dancedeets-hrd.appspot.com
python -m popular_people --log=DEBUG --project dancedeets-hrd --job-name=popular-people --runner DataflowRunner --staging_location $BUCKET/staging --temp_location $BUCKET/temp --output $BUCKET/output --sdk_location $SDK --setup_file ./setup.py --num_workers=20

"""

site.addsitedir('lib')

logging.basicConfig(level=logging.DEBUG)

from google.cloud import datastore
from google.cloud.datastore import query
from google.cloud.datastore import helpers

import apache_beam as beam
from apache_beam import pvalue
from apache_beam import typehints
from apache_beam.io.gcp.datastore.v1.datastoreio import ReadFromDatastore
from apache_beam.io.gcp.datastore.v1.datastoreio import WriteToDatastore
from apache_beam.metrics import Metrics
from apache_beam.utils.pipeline_options import GoogleCloudOptions
from apache_beam.utils.pipeline_options import PipelineOptions
from apache_beam.utils.pipeline_options import SetupOptions


TOP_ALL_N = 1000
TOP_CITY_N = 100

TOP_ATTENDEE = 'TA_MARK'

def ConvertToEntity(element):
    return helpers.entity_from_protobuf(element)

def CountableEvent(db_event):
    # Don't use auto-events to train...could have a runaway AI system there!
    #TODO: Use Constants
    if ':' in db_event.key.name:
        namespace = db_event.key.name.split(':')[0]
    else:
        namespace = 'FB'
    if namespace == 'FB' and db_event['creating_method'] != 'CM_AUTO_ATTENDEE':
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

def DebugExportEventAttendeesForGrouping(data):
    key = data.copy()
    del key['person_name'] # Don't need
    del key['event_id']
    del key['count_once_per']
    # key = {person_type, city, category, person_id, count_once_per}
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
    for person in sorted_people:
        new_key = key.copy()
        new_key['person_id'] = person['person_id']
        # new_key contains {person_type, city, category, person_id}
        yield new_key, TOP_ATTENDEE

def DebugFilterForTopAttendee((key, values)):
    values = list(values)
    if random.random() < 0.01:
        logging.info('got0 %r', (key, values))
    if TOP_ATTENDEE in values:
        if random.random() < 0.1:
            logging.info('got1 %r', (key, values))
        new_values = [x for x in values if x != TOP_ATTENDEE]
        if len(new_values) != 1:
            logging.info('got2 %r', (key, values))
            logging.error('Key %s had unexpected trimmed new_values length == %s, values: %s', key, len(new_values), new_values)
        else:
            yield key, new_values[0]

class DebugBuildPRDebugAttendee(beam.DoFn):
    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, (key, grouped_events), timestamp):
        key_name = '%s: %s' % (key['city'], key['person_id'])
        db_key = self.client.key('PRDebugAttendee', key_name)
        debug_attendee = datastore.Entity(key=db_key, exclude_from_indexes=['grouped_event_ids'])
        debug_attendee['created_date'] = timestamp

        debug_attendee['city'] = key['city']
        debug_attendee['person_id'] = key['person_id']
        debug_attendee['grouped_event_ids'] = json.dumps(grouped_events)
        yield debug_attendee

def ToJson(value):
    yield json.dumps(value, sort_keys=True)

def ToJsonKeys((key, value)):
    yield json.dumps(key, sort_keys=True), value

def FromJson(value):
    yield json.loads(value)

def FromJsonKeys((key, value)):
    yield (json.loads(key), value)

def GroupAttendeesByCategory(data):
    #logging.debug('GroupAttendeesByCategory: %r', value)
    new_key = data.copy()
    del new_key['event_id'] # Don't need
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

    sorted_counts = sorted(people_counts.iteritems(), key=lambda (person_id, count): -count)
    sorted_people = [{
        'person_id': pid,
        'person_name': person_lookup[pid],
        'count': count,
    } for pid, count in sorted_counts]
    yield (key, sorted_people[:TOP_ALL_N])

def CityToCategoryPeople((key, people)):
    within_city_category = {
        'category': key['category'],
        'person_type': key['person_type'],
    }
    yield (key['city'], [within_city_category, people])

class BuildPRCityCategory(beam.DoFn):
    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, (key, sorted_people), timestamp):
        key_name = '%s: %s: %s' % (key['person_type'], key['city'], key['category'])
        db_key = self.client.key('PRCategoryCity', key_name)
        ranking = datastore.Entity(key=db_key, exclude_from_indexes=['top_people_json'])
        ranking['created_date'] = timestamp

        ranking['person_type'] = key['person_type']
        ranking['city'] = key['city']
        ranking['category'] = key['category']
        ranking['top_people_json'] = json.dumps(sorted_people)
        yield ranking

class BuildPRCity(beam.DoFn):

    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, (city, category_and_people), timestamp):
        category_and_people = list(category_and_people)
        #logging.info('BuildPRCity: %r: %r', city, category_and_people)
        db_key = self.client.key('PRCity', city)
        ranking = datastore.Entity(key=db_key, exclude_from_indexes=['category_and_people'])
        ranking['created_date'] = timestamp

        ranking['category_and_people'] = [json.dumps(x) for x in category_and_people[:TOP_CITY_N]]
        yield ranking

from google.cloud import exceptions

class WriteToDatastoreSingle(beam.DoFn):

    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, entity):
        try:
            self.client.put(entity)
        except exceptions.BadRequest:
            logging.error('Error putting %s', entity)

def ConvertFromEntity(entity):
    return helpers.entity_to_protobuf(entity)

def Logger(entity, prefix):
    logging.info('%s: %r', prefix, entity)
    yield entity

run_locally = False

def read_from_datastore(project, pipeline_options):
    """Creates a pipeline that reads entities from Cloud Datastore."""
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
    produce_attendees = (p
        | 'read from datastore' >> ReadFromDatastore(project, query._pb_from_query(q), num_splits=400)
        | 'convert to entity' >> beam.Map(ConvertToEntity)
        # Find the events we want to count, and expand all the admins/attendees
        | 'filter events' >> beam.FlatMap(CountableEvent)
        | 'load fb attending' >> beam.ParDo(GetEventAndAttending())
        | 'export attendees' >> beam.FlatMap(ExportPeople)
    )


    top_attendee_lists = (produce_attendees
        | 'group people by city' >> beam.FlatMap(GroupAttendeesByCategory)
        | 'group people by city-category' >> beam.GroupByKey()
        | 'build top-attendee lists' >> beam.FlatMap(CountPeopleInfos)
    )

    attendee_event_debugging = (produce_attendees
        # TODO: I think doing the admin-hash grouping inside the city-attendee grouping, will be muuuuuch faster (due to avoiding the shuffling)
        | 'regroup by City-Attendee' >> beam.FlatMap(DebugExportEventAttendeesForGrouping)
            #.with_output_types(typehints.Tuple[typehints.Dict[str, str], typehints.Tuple[str, typehints.List[str]]])
        | 'group by City-Attendee' >> beam.GroupByKey()
        | 'group event_ids' >> beam.FlatMap(DebugGroupEventIds)
            #.with_output_types(typehints.KV[typehints.Dict[str, str], typehints.Iterable[typehints.Tuple[str, typehints.List[str]]]])
    )

    exploded_top_attendees = (top_attendee_lists
        | 'explode the top attendees into the correct combo format' >> beam.FlatMap(DebugExplodeAttendeeList)
            #.with_output_types(typehints.KV[typehints.Dict[str, str], str])
    )

    good_attendee_event_debugging = (
        # These both have the same keys:
        # key contains {person_type, city, category, person_id}
        (attendee_event_debugging, exploded_top_attendees)
        | beam.Flatten()
        # This is necessary so that they both have unicode keys (or not), and so will GroupBYKey correctly
        | 'serialize dicts for unicode' >> beam.FlatMap(ToJsonKeys)
        | 'unserialize dicts for unicode' >> beam.FlatMap(FromJsonKeys)
        | 'group the attendee-debug info with the is-it-a-top-attendee info' >> beam.GroupByKey()
        | 'filter for TOP_ATTENDEE' >> beam.FlatMap(DebugFilterForTopAttendee)
            #.with_output_types(typehints.KV[typehints.Dict[str, str], typehints.Iterable[typehints.Tuple[str, typehints.List[str]]]])
        | 'build PRDebugAttendee' >> beam.ParDo(DebugBuildPRDebugAttendee(), timestamp)
    )

    save_rankings_for_city_category = (top_attendee_lists
        | 'generate PRCityCategory database record' >> beam.ParDo(BuildPRCityCategory(), timestamp)
    )

    save_rankings_for_city = (top_attendee_lists
        | 'output with city as key' >> beam.FlatMap(CityToCategoryPeople)
        | 'group by city' >> beam.GroupByKey()
        # And save it all back to the database
        | 'generate PRCity database record' >> beam.ParDo(BuildPRCity(), timestamp)
    )

    if not run_locally:
        save_rankings_for_city_category | 'write PRCityCategory to datastore (unbatched)' >> beam.ParDo(WriteToDatastoreSingle())
        save_rankings_for_city | 'write PRCity to datastore (unbatched)' >> beam.ParDo(WriteToDatastoreSingle())
        good_attendee_event_debugging | 'write PRDebugAttendee to datastore (unbatched)' >> beam.ParDo(WriteToDatastoreSingle())
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
    pipeline_options = PipelineOptions(sys.argv)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    gcloud_options = pipeline_options.view_as(GoogleCloudOptions)
    read_from_datastore('dancedeets-hrd', gcloud_options)

if __name__ == '__main__':
    run()
