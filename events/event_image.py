import urllib2

from google.appengine.api import images

from util import fetch
from util import gcs

EVENT_IMAGE_BUCKET = 'TODO:asdasdasdasdasd'

class NotFoundError(Exception):
    pass

class DownloadError(Exception):
    pass

def _raw_get_image(db_event):
    image_url = db_event.full_image_url
    try:
        mimetype, response = fetch.fetch_data(image_url)
        return mimetype, response
    except urllib2.HTTPError as e:
        raise DownloadError(e.code)

#TODO:
# event image bucket
# how to pass in width/height

def _event_image_filename(event_id):
    return '%s.jpg' % event_id

def cache_image_and_get_size(event):
    mimetype, response = _raw_get_image(event)
    gcs.put_object(EVENT_IMAGE_BUCKET, _event_image_filename(event.event_id), response)

    img = images.Image(response)
    return img.width, img.height


def _render_image(event_id, operation):
    image_data = gcs.get_object(EVENT_IMAGE_BUCKET, _event_image_filename(event_id))
    img = images.Image(image_data)
    if operation:
        operation(img)
    final_img = img.execute_transforms(output_encoding=images.JPEG)
    return 'image/jpeg', final_img

def render(response, event_id):
    def fix_image_size(img):
        # resize(width=0, height=0, crop_to_fit=False, crop_offset_x=0.5, crop_offset_y=0.5, allow_stretch=False)
        img.resize(width=img.width, height=img.height)
    mimetype, final_img = _render_image(event_id, operation=fix_image_size)
    response.headers['Content-Type'] = mimetype
    response.out.write(final_img)
