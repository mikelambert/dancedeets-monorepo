import base_servlet
import fb_api

# How long to wait before retrying on a failure. Intended to prevent hammering the server.
RETRY_ON_FAIL_DELAY = 60

class LoadFriendListHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        friend_list_id = self.request.get('friend_list_id')
        self.fbl.get(fb_api.LookupFriendList, friend_list_id)
    post=get

