"""
Google Prediction API integration for event classification.

The batch processing jobs have been migrated to Cloud Run Jobs.
See:
- dancedeets.jobs.generate_training_data
- dancedeets.jobs.classify_events_ml

This module retains:
- get_predict_service(): Google Prediction API client
- get_training_features(): Feature extraction for ML
- predict(): Single event prediction
"""
import logging
import string

from dancedeets.events import event_locations

convert_chars = string.punctuation + '\r\n\t'
trans = str.maketrans(convert_chars, ' ' * len(convert_chars))


def strip_punctuation(s):
    """Remove punctuation from a string."""
    return s.translate(trans)


def get_training_features(potential_event, fb_event, fb_event_attending):
    """
    Extract training features from an event.

    Args:
        potential_event: PotentialEvent instance
        fb_event: Facebook event data
        fb_event_attending: Facebook event attending data

    Returns:
        Tuple of feature values
    """
    if 'owner' in fb_event['info']:
        owner_name = 'id%s' % fb_event['info']['owner']['id']
    else:
        owner_name = ''
    location = event_locations.get_address_for_fb_event(fb_event)
    if isinstance(location, str):
        location = location.encode('utf-8')

    def strip_text(s):
        if isinstance(s, str):
            s = s.encode('utf8')
        return strip_punctuation(s.decode('utf8') if isinstance(s, bytes) else s).lower()

    name = strip_text(fb_event['info'].get('name', ''))
    description = strip_text(fb_event['info'].get('description', ''))

    attending_data = fb_event_attending.get('attending', {}).get('data', [])
    attendee_list = ' '.join(['id%s' % x['id'] for x in attending_data])

    source_list = ' '.join('id%s' % x.id for x in potential_event.source_ids_only())

    # Currently only returning attendee_list (other features commented out in original)
    return (attendee_list,)
    # Full features would be:
    # return (potential_event.language, owner_name, location, name, description, attendee_list, source_list)


MAGIC_USER_ID = '100529355548393795594'


def get_predict_service():
    """
    Get the Google Prediction API service client.

    Note: This uses OAuth credentials stored in Datastore.
    """
    # TODO(lambert): we need to cache this somehow
    import httplib2
    from apiclient.discovery import build
    from oauth2client import appengine

    credentials = appengine.StorageByKeyName(
        appengine.CredentialsModel, MAGIC_USER_ID, 'credentials'
    ).get()
    http = credentials.authorize(httplib2.Http())

    service = build("prediction", "v1.5", http=http)
    return service


MODEL_NAME = 'dancedeets/training_data.english.csv'
DANCE_BIAS_MODEL_NAME = 'training20120513dance'
NOT_DANCE_BIAS_MODEL_NAME = 'training20120513nodance'


def predict(potential_event, fb_event, fb_event_attending, service=None):
    """
    Predict whether an event is a dance event.

    Args:
        potential_event: PotentialEvent instance
        fb_event: Facebook event data
        fb_event_attending: Facebook event attending data
        service: Optional prediction service (will be created if not provided)

    Returns:
        Tuple of (dance_bias_score, not_dance_bias_score)
    """
    body = {
        'input': {
            'csvInstance': get_training_features(
                potential_event, fb_event, fb_event_attending
            )
        }
    }
    logging.info("Dance Data: %r", body)

    service = service or get_predict_service()
    train = service.trainedmodels()

    dance_bias_prediction = train.predict(body=body, id=DANCE_BIAS_MODEL_NAME).execute()
    dance_bias_score = [
        x['score'] for x in dance_bias_prediction['outputMulti']
        if x['label'] == 'dance'
    ][0]

    not_dance_bias_prediction = train.predict(
        body=body, id=NOT_DANCE_BIAS_MODEL_NAME
    ).execute()
    not_dance_bias_score = [
        x['score'] for x in not_dance_bias_prediction['outputMulti']
        if x['label'] == 'dance'
    ][0]

    logging.info("Dance Result: %s", dance_bias_prediction)
    logging.info("NoDance Result: %s", not_dance_bias_prediction)
    logging.info("Dance Score: %s, NoDance Score: %s", dance_bias_score, not_dance_bias_score)

    return dance_bias_score, not_dance_bias_score
