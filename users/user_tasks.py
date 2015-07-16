
import logging

import base_servlet
import fb_api
from util import fb_mapreduce
from util import timings
from . import users

GET_FRIEND_APP_USERS = """
SELECT uid FROM user
WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = %s)
AND is_app_user = 1
"""

class LookupAppFriendUsers(fb_api.LookupType):
    # V2.0 CHANGE
    version = "v2.0"

    @classmethod
    def get_lookups(cls, object_id):
        return [('info', cls.fql_url(GET_FRIEND_APP_USERS % object_id))]

class TrackNewUserFriendsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        key = fb_api.generate_key(LookupAppFriendUsers, self.fb_uid)
        fb_result = self.fbl.fb.fetch_keys([key])
        app_friend_list = fb_result[key]['info']
        logging.info("app_friend_list is %s", app_friend_list)
        user_friends = users.UserFriendsAtSignup.get_or_insert(self.fb_uid)
        # V2.0 CHANGE, remove str() call
        user_friends.registered_friend_string_ids = [str(x['uid']) for x in app_friend_list['data']]
        user_friends.put()
    post=get

class LoadUserHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        load_users = users.User.get_by_ids(user_ids)
        load_fb_user(self.fbl, load_users[0])
    post=get

class ReloadAllUsersHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        fb_mapreduce.start_map(
            fbl=self.fbl,
            name='Load Users',
            handler_spec='users.user_tasks.map_load_fb_user',
            entity_kind='users.users.User',
        )
    post=get


@timings.timed
def yield_load_fb_user(fbl, user):
    if user.expired_oauth_token:
        logging.info("Skipping user %s (%s) due to expired access_token", user.fb_uid, user.full_name)
        return
    if not fbl.access_token:
        logging.info("Skipping user %s (%s) due to not having an access_token", user.fb_uid, user.full_name)
    try:
        fb_user = fbl.get(fb_api.LookupUser, user.fb_uid)
    except fb_api.ExpiredOAuthToken as e:
        logging.info("Auth token now expired, mark as such: %s", e)
        user.expired_oauth_token_reason = e.args[0]
        user.expired_oauth_token = True
        user.put()
        return
    else:
        user.compute_derived_properties(fb_user)
        user.put()
map_load_fb_user = fb_mapreduce.mr_user_wrap(yield_load_fb_user)
load_fb_user = fb_mapreduce.nomr_wrap(yield_load_fb_user)
