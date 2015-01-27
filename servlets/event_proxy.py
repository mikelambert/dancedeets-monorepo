
import fb_api
import webapp2

from events import eventdata
from events import users
from util import fetch

class ImageProxyHandler(webapp2.RequestHandler):
    """Proxies images for use by twitter, where it doesn't need to respect the FB cache server's /robots.txt."""

    def get(self, event_id):
        user = users.User.get_by_key_name(fb_api.USERLESS_UID)
        fbl = fb_api.FBLookup(None, user.fb_access_token)
        try:
            event = fbl.get(fb_api.LookupEvent, event_id)
        except fb_api.NoFetchedDataException:
            self.response.set_status(404)
            return

        cover = eventdata.get_largest_cover(event)
        if not cover:
            self.response.set_status(404)
            return

        mimetype, response = fetch.fetch_data(cover['source'])
        self.response.headers["Content-Type"] = mimetype
        self.response.out.write(response)
