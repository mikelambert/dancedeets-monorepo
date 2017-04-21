
import logging

import app
import base_servlet
import fb_api
import mailchimp
from util import fb_mapreduce
from . import users


class LookupAppFriendUsers(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [('info', cls.url('%s/friends' % object_id))]


@app.route('/tasks/track_newuser_friends')
class TrackNewUserFriendsHandler(base_servlet.BaseTaskFacebookRequestHandler):
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
    user_operation = lambda self, fbl, load_users: [load_fb_user(fbl, x) for x in load_users]


@app.route('/tasks/reload_all_users')
class ReloadAllUsersHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        mailchimp_list_id = mailchimp.get_list_id()
        fb_mapreduce.start_map(
            fbl=self.fbl,
            name='Load Users',
            handler_spec='users.user_tasks.map_load_fb_user',
            entity_kind='users.users.User',
            extra_mapper_params={
                'mailchimp_list_id': mailchimp_list_id,
            }
        )
    post = get

#TODO: temp code, delete after running
@app.route('/tasks/fix_users')
class FixupUsersHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        fb_mapreduce.start_map(
            fbl=self.fbl,
            name='Load Users',
            handler_spec='users.user_tasks.map_fixup_user',
            entity_kind='users.users.User',
        )
    post = get

def yield_fixup_user(fbl, user):
    import datetime
    logging.info('User %s (%s) created %s with clients: %s', user.fb_uid, user.full_name, user.creation_time, user.clients)
    if user.creation_time and user.creation_time > datetime.datetime(2015, 1, 1):
        if set(['android', 'ios', 'react-android', 'react-ios']).intersection(user.clients):
            logging.info('Setting send_email for user %s (%s)!', user.fb_uid, user.full_name)
            user.send_email = True
            user.put()

map_fixup_user = fb_mapreduce.mr_user_wrap(yield_fixup_user)
fixup_user = fb_mapreduce.nomr_wrap(yield_fixup_user)

def yield_load_fb_user(fbl, user):
    if user.expired_oauth_token:
        logging.info('Skipping user %s (%s) due to expired access_token', user.fb_uid, user.full_name)
        users.update_mailchimp(user)
    elif not fbl.access_token:
        logging.info('Skipping user %s (%s) due to not having an access_token', user.fb_uid, user.full_name)
        users.update_mailchimp(user)
    else:
        fetch_and_save_fb_user(fbl, user)
        # The above function calls user.put(), so no need for:
        # users.update_mailchimp(user)


def fetch_and_save_fb_user(fbl, user):
    try:
        fb_user = fbl.get(fb_api.LookupUser, user.fb_uid)
    except fb_api.ExpiredOAuthToken as e:
        logging.info('Auth token now expired, mark as such: %s', e)
        user.expired_oauth_token_reason = e.args[0]
        user.expired_oauth_token = True
        user.put()
        return
    else:
        user.compute_derived_properties(fb_user)
        user.put()

map_load_fb_user = fb_mapreduce.mr_user_wrap(yield_load_fb_user)
load_fb_user = fb_mapreduce.nomr_wrap(yield_load_fb_user)
