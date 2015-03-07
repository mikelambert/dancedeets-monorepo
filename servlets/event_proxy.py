
import webapp2

from events import eventdata
from util import fetch

class ImageProxyHandler(webapp2.RequestHandler):
    """Proxies images for use by twitter, where it doesn't need to respect the FB cache server's /robots.txt."""

    def get(self, event_id):
        db_event = eventdata.DBEvent.get_by_id(event_id)        
        cover = eventdata.get_largest_cover(db_event.fb_event)
        if not cover:
            self.response.set_status(404)
            return

        mimetype, response = fetch.fetch_data(cover['source'])
        self.response.headers["Content-Type"] = mimetype
        self.response.out.write(response)
