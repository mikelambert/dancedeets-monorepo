import urllib2

from google.appengine.api import images

from util import fetch
from util import gcs

EVENT_IMAGE_BUCKET = 'dancedeets-event-images'

class DownloadError(Exception):
    pass

NotFoundError = gcs.NotFoundError

def _raw_get_image(db_event):
    image_url = db_event.full_image_url
    try:
        mimetype, response = fetch.fetch_data(image_url)
        return mimetype, response
    except urllib2.HTTPError as e:
        raise DownloadError(e.code)

def _event_image_filename(event_id):
    return '%s.jpg' % event_id

def cache_image_and_get_size(event):
    mimetype, response = _raw_get_image(event)
    gcs.put_object(EVENT_IMAGE_BUCKET, _event_image_filename(event.id), response)

    img = images.Image(response)
    return img.width, img.height


def _render_image(event_id):
    image_data = gcs.get_object(EVENT_IMAGE_BUCKET, _event_image_filename(event_id))
    return 'image/jpeg', image_data

def render(response, event):
    try:
        mimetype, final_img = _render_image(event.id)
    except NotFoundError:
        cache_image_and_get_size(event)
        mimetype, final_img = _render_image(event.id)
    response.headers['Content-Type'] = mimetype
    response.out.write(final_img)
