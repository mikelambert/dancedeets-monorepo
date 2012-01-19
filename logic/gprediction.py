import csv
import logging
import string
import StringIO

from events import eventdata
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

    # TODO(lambert): ideally would use keys_only=True, but that's not supported on get_by_key_name :-(
    db_events = eventdata.get_cached_db_events([x.fb_event_id for x in pevents])
    good_event_ids = [x.fb_event_id for x in db_events if x]

    csv_file = StringIO.StringIO()
    csv_writer = csv.writer(csv_file)

    for potential_event in pevents:
        try:
            good_event = potential_event.fb_event_id in good_event_ids and 'dance' or 'nodance'

            fb_event = batch_lookup.data_for_event(potential_event.fb_event_id)
            if fb_event['deleted']:
                continue
            fb_event_attending = batch_lookup.data_for_event_attending(potential_event.fb_event_id)

            training_features = get_training_features(potential_event, fb_event, fb_event_attending)
            csv_writer.writerow([good_event] + list(training_features))
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

    #TODO(lambert): someday write this as a proper mapreduce that reduces across languages and builds a classifier model per language?
    # for now we can just grep and build sub-models per-language on my client machine.
    return (potential_event.language, owner_name, location, name, description, attendee_list, source_list)


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

MAGIC_USER_ID = '100529355548393795594'

def get_predict_service():
    import httplib2
    from apiclient.discovery import build
    from oauth2client import appengine

    credentials = appengine.StorageByKeyName(appengine.CredentialsModel, MAGIC_USER_ID, 'credentials').get()
    http = credentials.authorize(httplib2.Http())

    service = build("prediction", "v1.4", http=http)
    return service

MODEL_NAME = 'dancedeets/training_data.english.csv'
def predict(potential_event, fb_event, fb_event_attending, service=None):
    if potential_event.language == 'en':
        body = {'input': {'csvInstance': get_training_features(potential_event, fb_event, fb_event_attending)}}
        service = service or get_predict_service()
        train = service.trainedmodels()
        prediction = train.predict(body=body, id=MODEL_NAME).execute()
        multi = prediction['outputMulti']
        dance_score = [x['score'] for x in multi if x['label'] == 'dance'][0]
        nodance_score = [x['score'] for x in multi if x['label'] == 'nodance'][0]
        logging.info("Dance Score: %s, NoDance Score: %s", dance_score, nodance_score)
        if 1.0 - (dance_score + nodance_score) > 0.01:
            logging.error("dance score and no dance score do not sum to 1.0")
        return dance_score
    else:
        return None

