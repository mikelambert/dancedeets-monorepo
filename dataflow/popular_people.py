import json
import logging
import os
import random
import site
import sys

"""
pip install 'git+https://github.com/apache/beam.git#egg=1.0&subdirectory=sdks/python' -t lib
pip install googledatastore -t lib
pip install google-cloud-datastore --user (cant use lib/)

python -m popular_people --log=DEBUG
"""

# Hack to fix serialization issues
os.environ['GOOGLE_CLOUD_DISABLE_GRPC'] = 'true'

site.addsitedir('lib')

logging.basicConfig(level=logging.DEBUG)

from google.cloud import datastore
from google.cloud.datastore import query
from google.cloud.datastore import helpers

import apache_beam as beam
from apache_beam.io.gcp.datastore.v1.datastoreio import ReadFromDatastore
from apache_beam.io.gcp.datastore.v1.datastoreio import WriteToDatastore
from apache_beam.metrics import Metrics
from apache_beam.utils.pipeline_options import GoogleCloudOptions
from apache_beam.utils.pipeline_options import PipelineOptions
from apache_beam.utils.pipeline_options import SetupOptions


def styles():
    class Style(object):
        def __init__(self, index_name, public_name):
            self.index_name = index_name
            self.public_name = public_name

        def __repr__(self):
            return 'Style(%s, %s)' % (self.index_name, self.public_name)

        @property
        def url_name(self):
            return self.public_name.lower()

    BREAK = Style('BREAK', 'Breaking')
    HIPHOP = Style('HIPHOP', 'Hip-Hop')
    HOUSE = Style('HOUSE', 'House')
    POP = Style('POP', 'Popping')
    LOCK = Style('LOCK', 'Locking')
    WAACK = Style('WAACK', 'Waacking')
    DANCEHALL = Style('DANCEHALL', 'Dancehall')
    VOGUE = Style('VOGUE', 'Vogue')
    KRUMP = Style('KRUMP', 'Krumping')
    TURF = Style('TURF', 'Turfing')
    LITEFEET = Style('LITEFEET', 'Litefeet')
    FLEX = Style('FLEX', 'Flexing')
    BEBOP = Style('BEBOP', 'Bebop')
    ALLSTYLE = Style('ALLSTYLE', 'All-Styles')

    STYLES = [
        BREAK,
        HIPHOP,
        HOUSE,
        POP,
        LOCK,
        WAACK,
        DANCEHALL,
        VOGUE,
        KRUMP,
        TURF,
        LITEFEET,
        FLEX,
        BEBOP,
        ALLSTYLE,
    ]
    return STYLES

#TODO: Use Constants
STYLES_SET = set(x.index_name for x in styles())

TOP_N = 100

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
        fb_event = json.loads(db_event['fb_event'])
        if not fb_event['empty']:
            yield db_event, fb_event

def GetEventAndAttending((db_event, fb_event), client):
    key = client.key('FacebookCachedObject', '701004.%s.OBJ_EVENT_ATTENDING' % db_event.key.name)
    fb_event_attending_record = client.get(key)
    if fb_event_attending_record and 'json_data' in fb_event_attending_record:
        fb_event_attending = json.loads(fb_event_attending_record['json_data'])
        if not fb_event_attending['empty']:
            yield db_event, fb_event, fb_event_attending

def CountPeople((db_event, fb_event, fb_event_attending)):
    # Count admins
    fb_info = fb_event['info']
    admins = fb_info.get('admins', {}).get('data')
    if not admins:
        if fb_info.get('owner'):
            admins = [fb_info.get('owner')]
        else:
            admins = []

    for admin in admins:
        for y in track_person('ADMIN', db_event, admin):
            yield y

    # Count attendees
    admin_hash = fb_info.get('owner', {}).get('id', random.random())

    # We don't want to use the 'maybe' lists in computing who are the go-to people for each city/style,
    # because they're not actually committed to these events.
    # Those who have committed to going should be the relevant authorities.
    try:
        attending = fb_event_attending['attending']['data']
    except KeyError:
        logging.error('Error loading attending for event %s: %s', fb_info['id'], fb_event_attending)
        return

    for attendee in attending:
        for y in track_person('ATTENDEE', db_event, attendee, admin_hash):
            yield y

def track_person(person_type, db_event, person, count_once_per=None):
    """Yields json({person-type, category, city}) to 'count_once_per: id: name' """
    if count_once_per is None:
        # This is a nice way to ensure each id counts once per...id
        # (ie, every id counts)
        count_once_per = person['id']

    people_info = {
        'count_once_per': count_once_per,
        'person': '%s: %s' % (person['id'], person.get('name')),
    }
    # Not using db_event.nearby_city_names since it's way too slow.
    # And we just search-many-cities on lookup time.
    for city in [db_event['city_name']]:
        key = {
            'person_type': person_type,
            'category': '',
            'city': city,
        }
        yield (key, people_info)
        for category in STYLES_SET.intersection(db_event.get('auto_categories', [])):
            key = {
                'person_type': person_type,
                'category': category,
                'city': city,
            }
            yield (key, people_info)

def CountPeopleInfos((key, people_infos)):
    counts = {}
    for person_info in people_infos:
        person_name = person_info['person']
        if person_name in counts:
            counts[person_name].add(person_info['count_once_per'])
        else:
            counts[person_name] = set([person_info['person']])
    count_list = [[person_json, len(unique_organizers)] for (person_json, unique_organizers) in counts.iteritems()]
    # count_list is [['id: name', count_of_unique_organizers], ...]
    sorted_counts = sorted(count_list, key=lambda kv: -kv[1])
    return (key, sorted_counts[:TOP_N])

def BuildPeopleRanking((key, top_n_counts), client):
    key_name = '%s: %s: %s' % (key['person_type'], key['city'], key['category'])
    db_key = client.key('PeopleRanking', key_name)
    ranking = datastore.Entity(key=db_key)

    ranking['person_type'] = key['person_type']
    ranking['city'] = key['city']
    ranking['category'] = key['category']
    ranking['top_people_json'] = top_n_counts
    return ranking

def ConvertFromEntity(entity):
    print entity
    return helpers.entity_to_protobuf(entity)

def read_from_datastore(project, pipeline_options):
    """Creates a pipeline that reads entities from Cloud Datastore."""
    p = beam.Pipeline(options=pipeline_options)
    # Create a query to read entities from datastore.
    client = datastore.Client()
    q = client.query(kind='DBEvent')

    run_locally = True
    if run_locally:
        q.key_filter(client.key('DBEvent', '99'), '>')
        q.key_filter(client.key('DBEvent', 'A'), '<')

    # Set up our map/reduce pipeline
    (p
        | 'read from datastore' >> ReadFromDatastore(project, query._pb_from_query(q))
        | 'convert to entity' >> beam.Map(ConvertToEntity)
        # Find the events we want to count, and expand all the admins/attendees
        | 'filter events' >> beam.FlatMap(CountableEvent)
        | 'load fb attending' >> beam.FlatMap(GetEventAndAttending, client)
        | 'count people' >> beam.FlatMap(CountPeople)
        # Group them and count most popular people per city-category
        | 'group by city-category' >> beam.GroupByKey()
        | 'count by city-category' >> beam.Map(CountPeopleInfos)
        # And save it all back to the database
        | 'generate database record' >> beam.Map(BuildPeopleRanking, client)
        | 'convert from entity' >> beam.Map(ConvertFromEntity)
        #| 'write to datastore' >> WriteToDatastore(client.project)
    )

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
