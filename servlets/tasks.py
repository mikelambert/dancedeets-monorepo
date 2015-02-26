
import logging
import webapp2

from google.appengine.api import mail

import base_servlet
from events import eventdata
from events import users
import fb_api
from logic import backgrounder
from logic import fb_reloading
from logic import pubsub
from logic import rankings
from logic import thing_scraper
from util import timings

# How long to wait before retrying on a failure. Intended to prevent hammering the server.
RETRY_ON_FAIL_DELAY = 60

GET_FRIEND_APP_USERS = """
SELECT uid FROM user
WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = %s)
AND is_app_user = 1
"""

class LookupAppFriendUsers(fb_api.LookupType):
    # V2.0 CHANGE
    version = "v1.0"

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

class LoadFriendListHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        friend_list_id = self.request.get('friend_list_id')
        self.fbl.get(fb_api.LookupFriendList, friend_list_id)
    post=get

class LoadEventHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        db_events = [x for x in eventdata.DBEvent.get_by_ids(event_ids) if x]
        fb_reloading.load_fb_event(self.fbl, db_events)
    post=get

class LoadEventAttendingHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        db_events = [x for x in eventdata.DBEvent.get_by_ids(event_ids) if x]
        fb_reloading.load_fb_event_attending(self.fbl, db_events)
    post=get

class LoadUserHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        load_users = users.User.get_by_key_name(user_ids)
        fb_reloading.load_fb_user(self.fbl, load_users[0])
    post=get

class ReloadAllUsersHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        fb_reloading.mr_load_fb_user(self.fbl)
    post=get

class ReloadPastEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        fb_reloading.mr_load_past_fb_event(self.fbl)
    post=get

class ReloadFutureEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        fb_reloading.mr_load_future_fb_event(self.fbl)
    post=get

class ReloadAllEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        fb_reloading.mr_load_all_fb_event(self.fbl)
    post=get

class ComputeRankingsHandler(webapp2.RequestHandler):
    def get(self):
        rankings.begin_ranking_calculations()

class LoadAllPotentialEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        fb_reloading.mr_load_potential_events(self.fbl)

class LoadPotentialEventsForFriendsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        friend_lists = []
        #TODO(lambert): extract this out into some sort of dynamic lookup based on Mike Lambert
        friend_lists.append('530448100598') # Freestyle SF
        friend_lists.append('565645040648') # Freestyle NYC
        friend_lists.append('10100136378543108') # Freestyle Asia
        friend_lists.append('10100415076510148') # Freestyle Boston
        friend_lists.append('734193578028') # Freestyle Japan
        friend_lists.append('612289903968') # Freestyle Socal
        friend_lists.append('646041540418') # Freestyle Europe
        friend_lists.append('583877258138') # Freestyle Elsewhere
        friend_lists.append('565645070588') # Choreo SF
        friend_lists.append('556389713398') # Choreo LA
        friend_lists.append('565645155418') # Choreo Elsewhere
        print self.fbl.access_token
        for fl_id, fl in zip(friend_lists, self.fbl.get_multi(fb_api.LookupFriendList, friend_lists, allow_cache=False)):
            logging.info("Friend list %s: Searching %s friends for events", fl_id, len(fl['friend_list']['data']))
            friend_ids = [x['id'] for x in fl['friend_list']['data']]
            backgrounder.load_potential_events_for_friends(self.fb_uid, friend_ids, allow_cache=self.allow_cache)

class LoadPotentialEventsFromWallPostsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        min_potential_events = int(self.request.get('min_potential_events', '0'))
        queue = self.request.get('queue', 'super-slow-queue')
        thing_scraper.mapreduce_scrape_all_sources(self.fbl, min_potential_events=min_potential_events, queue=queue)

class LoadPotentialEventsForUserHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        fb_reloading.load_potential_events_for_user_ids(self.fbl, user_ids)

class SocialPublisherHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        pubsub.pull_and_publish_event(self.fbl)

class PostJapanEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        token_nickname = self.request.get('token_nickname', None)
        fb_reloading.mr_post_jp_events(self.fbl, token_nickname)

class TimingsKeepAlive(base_servlet.BaseTaskRequestHandler):
    def get(self):
        timings.keep_alive()

class TimingsProcessDay(base_servlet.BaseTaskRequestHandler):
    def get(self):
        summary = timings.summary()
        sorted_summary = sorted(summary.items(), key=lambda x: x[1])
        summary_lines = []
        for key, value in sorted_summary:
            summary_line = '%s: %sms' % (key, value)
            self.response.out.write('%s\n' % summary_line)
            logging.info(summary_line)
            summary_lines.append(summary_line)

        # email!
        if self.request.get('to') and self.request.get('sender'):
            mail.send_mail(
                to=self.request.get('to'),
                sender=self.request.get('sender'),
                subject="instance usage for the day",
                body='\n'.join(summary_lines)
            )
        timings.clear_all()

