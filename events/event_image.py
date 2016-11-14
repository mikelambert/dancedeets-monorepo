import urllib2

from events import eventdata
from util import fetch

class NotFoundError(Exception):
    pass

class DownloadError(Exception):
    pass

def get_image(event_id):
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
