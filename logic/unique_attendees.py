from mapreduce import mapreduce_pipeline

import fb_api
from util import fb_mapreduce

def map_each_attendee(db_event):
    fbl = fb_mapreduce.get_fblookup()
    fbl.request(fb_api.LookupEventAttending, db_event.fb_event_id)
    fbl.batch_fetch()
    fb_event_attending = fbl.fetched_data(fb_api.LookupEventAttending, db_event.fb_event_id)
    for attendee in fb_event_attending['attending']['data']:
        yield (db_event.city_name, attendee['id'])

def reduce_just_unique_attendees(city, all_attendees):
    yield (city, len(set(all_attendees)))

def mr_count_attendees_per_city(fbl):
    mrp = mapreduce_pipeline.MapreducePipeline( 
        'unique_attendees',
        'logic.unique_attendees.map_each_attendee',
        'logic.unique_attendees.reduce_just_unique_attendees',
        'mapreduce.input_readers.DatastoreInputReader',
        'mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        mapper_params={
            'entity_kind': 'events.eventdata.DBEvent',
            'fbl_fb_uid': fbl.fb_uid,
            'fbl_access_token': fbl.access_token,
            'fbl_allow_cache': fbl.allow_cache,
        },
        reducer_params={'mime_type': 'text/plain'},
        shards=2,
    )
    mrp.start()
    return mrp

