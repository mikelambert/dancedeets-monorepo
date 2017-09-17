from __future__ import absolute_import

from dancedeets.servlets import api
from . import db


@api.apiroute(r'/favorites')
class RsvpAjaxHandler(api.ApiHandler):
    def get(self):
        favorite_event_ids = db.get_favorite_event_ids_for_user(user_id=self.fbl.fb_uid)
        favorites_json = {'favorites': favorite_event_ids}
        self.write_json_success(favorites_json)

    def post(self):
        if self.json_body:
            event_id = self.json_body.get('event_id')
        else:
            event_id = self.request.get('event_id')
        db.add_favorite(self.fbl.fb_uid, event_id)
        self.write_json_success()

    def delete(self):
        if self.json_body:
            event_id = self.json_body.get('event_id')
        else:
            event_id = self.request.get('event_id')
        db.delete_favorite(self.fbl.fb_uid, event_id)
        self.write_json_success()
