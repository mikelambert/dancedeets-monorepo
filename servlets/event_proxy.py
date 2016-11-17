
import webapp2

import app
from events import eventdata
from events import event_image


@app.route(r'/events/image_proxy/(%s)/?' % eventdata.EVENT_ID_REGEX)
class ImageProxyHandler(webapp2.RequestHandler):
    """Proxies images for use by twitter, where it doesn't need to respect the FB cache server's /robots.txt."""

    def get(self, event_id):
        db_event = eventdata.DBEvent.get_by_id(event_id)
        if not db_event:
            self.response.set_status(404)
            return
        try:
            mimetype, response = event_image._raw_get_image(db_event)
        except event_image.NotFoundError:
            self.response.set_status(404)
            return
        except event_image.DownloadError as e:
            self.response.status = e.code
            return

        self.response.headers['Content-Type'] = mimetype
        self.response.out.write(response)
