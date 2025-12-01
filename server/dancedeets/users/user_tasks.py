"""
User management tasks.

The batch user refresh has been migrated to Cloud Run Jobs.
See: dancedeets.jobs.refresh_users

This module retains:
- LookupAppFriendUsers: FB API lookup type for friend tracking
- TrackNewUserFriendsHandler: Handler for tracking new user friends
- LoadUserHandler: Handler for loading specific users
- fetch_and_save_fb_user: Core function for FB user refresh
"""
import logging

from dancedeets import app
from dancedeets import base_servlet
from dancedeets import fb_api
from dancedeets.users import users


class LookupAppFriendUsers(fb_api.LookupType):
    """FB API lookup type for getting app friends."""
    @classmethod
    def get_lookups(cls, object_id):
        return [('info', cls.url('%s/friends' % object_id))]


@app.route('/tasks/track_newuser_friends')
class TrackNewUserFriendsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    """Track friends for newly registered users."""
    def get(self):
        key = fb_api.generate_key(LookupAppFriendUsers, self.fb_uid)
        fb_result = self.fbl.fb.fetch_keys([key])
        app_friend_list = fb_result[key]['info']
        logging.info('app_friend_list is %s', app_friend_list)
        user_friends = users.UserFriendsAtSignup.get_or_insert(self.fb_uid)
        user_friends.registered_friend_string_ids = [x['id'] for x in app_friend_list['data']]
        user_friends.put()

    post = get


@app.route('/tasks/load_users')
class LoadUserHandler(base_servlet.UserOperationHandler):
    """Load specific users from Facebook."""
    user_operation = lambda self, fbl, load_users: [load_fb_user(fbl, x) for x in load_users]


def fetch_and_save_fb_user(fbl, user):
    """
    Fetch user data from Facebook and save to Datastore.

    This is the core function used by both:
    - Cloud Run Job: dancedeets.jobs.refresh_users
    - LoadUserHandler for individual user loading
    """
    try:
        fb_user = fbl.get(fb_api.LookupUser, user.fb_uid)
    except fb_api.ExpiredOAuthToken as e:
        logging.info('Auth token now expired, mark as such: %s', e)
        user.expired_oauth_token_reason = e.args[0] if e.args else "Unknown"
        user.expired_oauth_token = True
        user.put()
        return
    else:
        user.compute_derived_properties(fb_user)
        user.put()


def load_fb_user(fbl, user):
    """Load and save a single user (wrapper for non-mapreduce context)."""
    if user.expired_oauth_token:
        logging.info('Skipping user %s (%s) due to expired access_token', user.fb_uid, user.full_name)
        user.put()
    elif not fbl.access_token:
        logging.info('Skipping user %s (%s) due to not having an access_token', user.fb_uid, user.full_name)
        user.put()
    else:
        fetch_and_save_fb_user(fbl, user)
