import imghdr
import logging
try:
    from PIL import Image
    from resizeimage import resizeimage
except ImportError:
    logging.exception('Error importing PIL')
    Image = None
    resizeimage = None
import io
import urllib2

from google.appengine.api import images

from util import fetch
from util import gcs

EVENT_IMAGE_BUCKET = 'dancedeets-event-flyers-full'

def test_jpeg(h, f):
    if h[:4] in [
        '\xff\xd8\xff\xe2',
        '\xff\xd8\xff\xe1',
        '\xff\xd8\xff\xe0',
        '\xff\xd8\xff\xdb'
    ]:
        return 'jpeg'
imghdr.tests.append(test_jpeg)

class DownloadError(Exception):
    def __init__(self, code):
        super(DownloadError, self).__init__()
        self.code = code

NotFoundError = gcs.NotFoundError

def _raw_get_image(db_event):
    image_url = db_event.full_image_url
    try:
        logging.info('Fetching image for event %s: %s', db_event.id, image_url)
        mimetype, response = fetch.fetch_data(image_url)
        return mimetype, response
    except urllib2.HTTPError as e:
        raise DownloadError(e.code)

def _event_image_filename(event_id):
    return str(event_id)

def cache_image_and_get_size(event):
    mimetype, response = _raw_get_image(event)
    gcs.put_object(EVENT_IMAGE_BUCKET, _event_image_filename(event.id), response)

    img = images.Image(response)
    return img.width, img.height


def _render_image(event_id):
    image_data = gcs.get_object(EVENT_IMAGE_BUCKET, _event_image_filename(event_id))
    f = io.BytesIO(image_data)
    image_type = imghdr.what(f)
    return 'image/%s' % image_type, image_data

def _resize_image(final_image, width, height):
    if width or height:
        orig_data = io.BytesIO(final_image)
        with Image.open(orig_data) as image:
            resized = None
            if width and height:
                resized = resizeimage.resize_cover(image, [width, height])
            elif width:
                resized = resizeimage.resize_width(image, width)
            elif height:
                resized = resizeimage.resize_height(image, height)
            resized_data = io.BytesIO()
            resized.save(resized_data, image.format)
            final_image = resized_data.getvalue()
    return final_image

def render(response, event, width=None, height=None):
    try:
        mimetype, final_image = _render_image(event.id)
    except NotFoundError:
        cache_image_and_get_size(event)
        mimetype, final_image = _render_image(event.id)
    final_image = _resize_image(final_image, width, height)
    response.headers['Content-Type'] = mimetype
    response.out.write(final_image)
