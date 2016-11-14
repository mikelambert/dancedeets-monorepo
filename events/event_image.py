import urllib2

from google.appengine.api import images

from events import eventdata
from util import fetch
from util import gcs

EVENT_IMAGE_BUCKET = 'TODO:asdasdasdasdasd'

class NotFoundError(Exception):
    pass

class DownloadError(Exception):
    pass

def _raw_get_image(event_id):
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if not db_event:
        raise NotFoundError()
    cover = db_event.largest_cover
    if not cover:
        raise NotFoundError()

    try:
        mimetype, response = fetch.fetch_data(cover['source'])
        return mimetype, response
    except urllib2.HTTPError as e:
        raise DownloadError(e.code)


#TODO:
# event image bucket
# how to pass back image size/dimensions
# how to pass in width/height
# where to stick this code?

def _event_image_filename(event_id):
    return '%s.jpg' % event_id

def cache_image_and_get_size(event_id):
    mimetype, response = _raw_get_image(event_id)
    gcs.put_object(EVENT_IMAGE_BUCKET, _event_image_filename(event_id), response)

    img = images.Image(response)
    return img.width, img.height


def render_image(event_id, operation):
    image_data = gcs.get_object(EVENT_IMAGE_BUCKET, _event_image_filename(event_id))
    img = images.Image(image_data)
    if operation:
        operation(img)
    final_img = img.execute_transforms(output_encoding=images.JPEG)
    return 'image/jpeg', final_img

def render(self, event_id):
    def fix_image_size(img):
        img.resize(width=img.width, height=img.height)
    mimetype, final_img = render_image(event_id, operation=fix_image_size)
    self.response.headers['Content-Type'] = mimetype
    self.response.out.write(final_img)
