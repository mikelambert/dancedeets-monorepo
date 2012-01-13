import csv
import logging
import string
import StringIO

import fb_api
from logic import event_locations
from util import fb_mapreduce

convert_chars = string.punctuation + '\n\t'
trans = string.maketrans(convert_chars, ' ' * len(convert_chars))

def strip_punctuation(s):
    return s.translate(trans)

def training_data_for_pevents(batch_lookup, pevents):
    batch_lookup.allow_memcache_write = False # don't pollute memcache
    for potential_event in pevents:
        batch_lookup.lookup_event(potential_event.fb_event_id)
        batch_lookup.lookup_event_attending(potential_event.fb_event_id)
    batch_lookup.finish_loading()
    csv_file = StringIO.StringIO()
    csv_writer = csv.writer(csv_file)

    for potential_event in pevents:
        try:
            fb_event = batch_lookup.data_for_event(potential_event.fb_event_id)
            if fb_event['deleted']:
                continue
            fb_event_attending = batch_lookup.data_for_event_attending(potential_event.fb_event_id)

            training_features = get_training_features(potential_event, fb_event, fb_event_attending)
            csv_writer.writerow(training_features)
        except fb_api.NoFetchedDataException:
            logging.info("No data fetched for event id %s", potential_event.fb_event_id)
    yield csv_file.getvalue()
map_training_data_for_pevents = fb_mapreduce.mr_wrap(training_data_for_pevents)

def get_training_features(potential_event, fb_event, fb_event_attending):
    if 'owner' in fb_event['info']:
        owner_name = fb_event['info']['owner']['id']
    else:
        owner_name = ''
    if 'venue' in fb_event['info']:
        location = event_locations.venue_for_fb_location(fb_event['info']['venue'])
        location = (location or '').encode('utf8')
    else:
        location = ''
    def strip_text(s):
        return strip_punctuation(s.encode('utf8')).lower()
    name = strip_text(fb_event['info'].get('name', ''))
    description = strip_text(fb_event['info'].get('description', ''))

    attendee_list = ' '.join([x['id'] for x in fb_event_attending['attending']['data']])

    source_list = ' '.join(str(x) for x in potential_event.source_ids)

    #TODO(lambert): maybe include number-of-keywords and keyword-density?

    return (owner_name, location, name, description, attendee_list, source_list)


def mr_generate_training_data(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='Write Training Data',
        handler_spec='logic.gprediction.map_training_data_for_pevents',
        output_writer_spec='mapreduce.output_writers.BlobstoreOutputWriter',
        handle_batch_size=20,
        entity_kind='logic.potential_events.PotentialEvent',
        extra_mapper_params={'mime_type': 'text/plain'},
    )

