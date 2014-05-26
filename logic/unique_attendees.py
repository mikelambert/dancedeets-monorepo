from mapreduce import mapreduce_pipeline
from util import fb_mapreduce

def map_each_attendee(db_event):
    batch_lookup = fb_mapreduce.get_batch_lookup()
    batch_lookup.lookup_event_attending(db_event.fb_event_id)
    batch_lookup.finish_loading()
    fb_event_attending = batch_lookup.data_for_event_attending(db_event.fb_event_id)
    for attendee in fb_event_attending['attending']['data']:
        yield (db_event.city_name, attendee['id'])

def reduce_just_unique_attendees(city, all_attendees):
    yield (city, len(set(all_attendees)))

def mr_count_attendees_per_city(batch_lookup):
    mrp = mapreduce_pipeline.MapreducePipeline( 
        'unique_attendees',
        'logic.unique_attendees.map_each_attendee',
        'logic.unique_attendees.reduce_just_unique_attendees',
        'mapreduce.input_readers.DatastoreInputReader',
        'mapreduce.output_writers.BlobstoreOutputWriter',
        mapper_params={
            'entity_kind': 'events.eventdata.DBEvent',
            'batch_lookup_fb_uid': batch_lookup.fb_uid,
            'batch_lookup_access_token': batch_lookup.access_token,
            'batch_lookup_allow_cache': batch_lookup.allow_cache,

        },
        reducer_params={'mime_type': 'text/plain'},
        shards=2,
    )
    mrp.start()
    return mrp

