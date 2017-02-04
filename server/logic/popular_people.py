import logging

from mapreduce import mapreduce_pipeline

import app
import base_servlet
import event_types
import fb_api
from util import fb_mapreduce

"""
MAP
for each event:
    for each nearby city of event:
        for each attendee of event:
            export (cityname, attendee): event_id

REDDUCE:
foreach (cityname, attendee): event_ids:
    export cityname: (attendee, len(event_ids)1)


foreach cityname: (attendee, event_count):
    get top_N(attendee by event_count) in cityname:
        export top_N
"""

STYLES_SET = set(event_types.STYLES)

def track_person(grouping, db_event, person):
    logging.error('aaaa')
    person_name = ('%s: %s' % (person['id'], person.get('name'))).encode('utf-8')
    logging.info('%s: %s', grouping, person_name)
    for city in db_event.nearby_city_names:
        key = '%s: %s: %s' % (grouping, None, city)
        yield (key, person_name)
        logging.info('%s: %s', db_event.auto_categories, STYLES_SET.intersection(db_event.auto_categories))
        logging.info('%s', (key, person_name))
        for category in STYLES_SET.intersection(db_event.auto_categories):
            key = '%s: %s: %s' % (grouping, category, city)
            yield (key, person_name)
            logging.info('%s', (key, person_name))

BATCH_SIZE = 20
def output_people(db_events):
    db_events = [x for x in db_events if x.is_fb_event]

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

def reduce_popular_people(city_category, people):
    logging.info('%r', city_category)
    grouping, city, category = city_category.split(': ', 2)
    counts = {}
    for person in people:
        if person in counts:
            counts[person] += 1
        else:
            counts[person] = 1
    sorted_counts = sorted(counts.items(), key=lambda kv: -kv[1])
    logging.info('Top %s in %s for %s', grouping, city, category)
    for x in sorted_counts[:5]:
        logging.info('%s', x)

def mr_popular_people_per_city(fbl):
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
    mrp.start()
    return mrp

@app.route('/tools/popular_people')
class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        mr_popular_people_per_city(self.fbl)
