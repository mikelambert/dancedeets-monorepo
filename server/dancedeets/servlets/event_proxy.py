import webapp2

from dancedeets import app
from dancedeets.events import eventdata
from dancedeets.events import event_image
from dancedeets.util import urls


@app.route(r'/events/image_proxy/(%s)(?:/(\d+))/?' % urls.EVENT_ID_REGEX)
class ImageProxyHandler(webapp2.RequestHandler):
    """Proxies images for use by twitter, where it doesn't need to respect the FB cache server's /robots.txt."""

    def get(self, event_id, index=None):
        db_event = eventdata.DBEvent.get_by_id(event_id)
        if not db_event or not db_event.full_image_url:
            self.response.set_status(404)
            return
        width = self.request.get('width')
        if width:
            width = int(width)
        else:
            width = None
        height = self.request.get('height')
        if height:
            height = int(height)
        else:
            height = None
        try:
            event_image.render(self.response, db_event, index, width, height)
        except event_image.NotFoundError:
            self.response.set_status(404)
            return
        except event_image.DownloadError as e:
            self.response.status = e.code
            return
