
import urllib2
import webapp2

import app
from events import eventdata
from util import fetch


@app.route(r'/events/image_proxy/(%s)/?' % eventdata.EVENT_ID_REGEX)
class ImageProxyHandler(webapp2.RequestHandler):
    """Proxies images for use by twitter, where it doesn't need to respect the FB cache server's /robots.txt."""

    def get(self, event_id):
        db_event = eventdata.DBEvent.get_by_id(event_id)
        if not db_event:
            self.response.set_status(404)
            return
        cover = db_event.largest_cover
        if not cover:
            self.response.set_status(404)
            return

        try:
            mimetype, response = fetch.fetch_data(cover['source'])
            self.response.headers["Content-Type"] = mimetype
            self.response.out.write(response)
        except urllib2.HTTPError as e:
            self.response.status = e.code
