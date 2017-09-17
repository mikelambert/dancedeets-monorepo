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

from dancedeets.util import fetch
from dancedeets.util import gcs
from dancedeets.util import runtime

EVENT_IMAGE_BUCKET = 'dancedeets-event-flyers-full'
EVENT_IMAGE_CACHE_BUCKET = 'dancedeets-event-flyers-%s-by-%s'

CACHEABLE_SIZES = set([
    (180, 180),
    (720, None),
    # Some other common mobile image sizes
    #    (320, None),
    #    (1080, None),
    #    (1440, None),
])


def test_jpeg(h, f):
    if h[:4] in ['\xff\xd8\xff\xe2', '\xff\xd8\xff\xe1', '\xff\xd8\xff\xe0', '\xff\xd8\xff\xdb']:
        return 'jpeg'


imghdr.tests.append(test_jpeg)


class DownloadError(Exception):
    def __init__(self, code):
        super(DownloadError, self).__init__()
        self.code = code


class NoImageError(Exception):
    pass


NotFoundError = gcs.NotFoundError


def _raw_get_image(db_event):
    image_url = db_event.full_image_url
    # For testing purposes:
    if image_url.startswith('test:'):
        raise NotFoundError()
    if not image_url:
        raise NoImageError()
    try:
        logging.info('Fetching image for event %s: %s', db_event.id, image_url)
        mimetype, response = fetch.fetch_data(image_url)
        return mimetype, response
    except urllib2.HTTPError as e:
        raise DownloadError(e.code)
    except urllib2.URLError:
        raise DownloadError(404)


def _event_image_filename(event_id):
    return str(event_id)


def _clear_out_resize_caches(event_id):
    for width, height in CACHEABLE_SIZES:
        bucket = _get_cache_bucket_name(width, height)
        gcs.delete_object(bucket, _event_image_filename(event_id))


def cache_image_and_get_size(event):
    # For testing purposes:
    if event.full_image_url.startswith('test:'):
        return 100, 100
    else:
        mimetype, response = _raw_get_image(event)
        try:
            gcs.put_object(EVENT_IMAGE_BUCKET, _event_image_filename(event.id), response)
            _clear_out_resize_caches(event.id)
        except:
            if runtime.is_local_appengine():
                logging.exception('Error saving event image: %s', event.id)
            else:
                raise
        img = images.Image(response)
        return img.width, img.height


def _render_image(event_id):
    image_data = gcs.get_object(EVENT_IMAGE_BUCKET, _event_image_filename(event_id))
    return image_data


def _resize_image(final_image, width, height):
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


def _attempt_resize_image(final_image, width, height):
    try:
        if width or height:
            final_image = _resize_image(final_image, width, height)
    except resizeimage.ImageSizeError as e:
        logging.info('Requested too-large image resize, returning original image: %s', e)
    return final_image


def _get_cache_bucket_name(width, height):
    name = EVENT_IMAGE_CACHE_BUCKET % (width, height)
    return name.lower()


def _read_image_cache(event_id, width, height):
    try:
        image_data = gcs.get_object(_get_cache_bucket_name(width, height), _event_image_filename(event_id))
        return image_data
    except NotFoundError:
        return None


def _write_image_cache(event_id, width, height, final_image):
    bucket = _get_cache_bucket_name(width, height)
    filename = _event_image_filename(event_id)
    try:
        gcs.put_object(bucket, filename, final_image)
    except NotFoundError:
        logging.error('Error writing image cache to gs://%s/%s', bucket, filename)


def _get_mimetype(image_data):
    f = io.BytesIO(image_data)
    image_type = imghdr.what(f)
    return 'image/%s' % image_type


def get_image(event):
    try:
        final_image = _render_image(event.id)
    except NotFoundError:
        cache_image_and_get_size(event)
        final_image = _render_image(event.id)
    return final_image


def render(response, event, width=None, height=None):
    final_image = None
    cache_key = (width, height)
    logging.info('Cache key is %r', cache_key)
    if cache_key in CACHEABLE_SIZES:
        final_image = _read_image_cache(event.id, width, height)
    if not final_image:
        final_image = get_image(event)
    if width or height:
        try:
            final_image = _resize_image(final_image, width, height)
            if cache_key in CACHEABLE_SIZES:
                _write_image_cache(event.id, width, height, final_image)
        except resizeimage.ImageSizeError as e:
            logging.info('Requested too-large image resize, using original image: %s', e)
    response.headers['Content-Type'] = _get_mimetype(final_image)
    # Sometimes the event updates images, so we don't want to cache these for too long!
    response.headers['Cache-Control'] = 'public, max-age=%s' % (4 * 60 * 60)
    response.out.write(final_image)
