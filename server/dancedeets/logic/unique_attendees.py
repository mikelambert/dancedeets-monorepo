import logging

from mapreduce import mapreduce_pipeline

from dancedeets import app
from dancedeets import base_servlet
from dancedeets import fb_api
from dancedeets.util import fb_mapreduce

BATCH_SIZE = 20


def map_each_attendee(db_events):
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
        for attendee in fb_event_attending['attending']['data']:
            yield ('City: %s' % db_event.city_name, attendee['id'])
            yield ('Country: %s' % db_event.country, attendee['id'])


def reduce_just_unique_attendees(location, all_attendees):
    yield 'Unique Attendees in %s: %s\n' % (location, len(set(all_attendees)))
    yield 'Total RSVPs in %s: %s\n' % (location, len(all_attendees))


def mr_count_attendees_per_city(fbl):
    mapper_params = {
        'entity_kind': 'events.eventdata.DBEvent',
        'handle_batch_size': BATCH_SIZE,
    }
    mapper_params.update(fb_mapreduce.get_fblookup_params(fbl, randomize_tokens=True))
    mrp = mapreduce_pipeline.MapreducePipeline(
        'unique_attendees',
        'logic.unique_attendees.map_each_attendee',
        'logic.unique_attendees.reduce_just_unique_attendees',
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


@app.route('/tools/unique_attendees')
class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        mr_count_attendees_per_city(self.fbl)
