
import webapp2

import app
from events import eventdata
from events import event_image


@app.route(r'/events/image_proxy/(%s)/?' % eventdata.EVENT_ID_REGEX)
class ImageProxyHandler(webapp2.RequestHandler):
    """Proxies images for use by twitter, where it doesn't need to respect the FB cache server's /robots.txt."""

    def get(self, event_id):
        db_event = eventdata.DBEvent.get_by_id(event_id)
        if not db_event or not db_event.full_image_url:
            self.response.set_status(404)
            return
        width = self.request.get('width')
        if width: width = int(width)
        height = self.request.get('height')
        if height: height = int(height)
        try:
            event_image.render(self.response, db_event, width, height)
        except event_image.NotFoundError:
            self.response.set_status(404)
            return
        except event_image.DownloadError as e:
            self.response.status = e.code
            return
