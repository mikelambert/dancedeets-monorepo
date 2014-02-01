
import cgi
import datetime
import logging
import re
import time
import urllib
import urlparse
import webapp2

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.runtime import apiproxy_errors


import base_servlet
from events import eventdata
from events import users
import facebook
import fb_api
from logic import backgrounder
from logic import email_events
from logic import fb_reloading
from logic import potential_events
from logic import rankings
from logic import search
from logic import thing_db
from logic import thing_scraper
from util import timings

# How long to wait before retrying on a failure. Intended to prevent hammering the server.
RETRY_ON_FAIL_DELAY = 60

GET_FRIEND_APP_USERS = """
SELECT uid FROM user
WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = %s)
AND is_app_user = 1
"""

class BaseTaskRequestHandler(webapp2.RequestHandler):
    pass

class BaseTaskFacebookRequestHandler(BaseTaskRequestHandler):
    def requires_login(self):
        return False

    def initialize(self, request, response):
        return_value = super(BaseTaskFacebookRequestHandler, self).initialize(request, response)

        self.fb_uid = int(self.request.get('user_id'))
        self.user = users.User.get_cached(self.fb_uid)
        if self.user:
            assert self.user.fb_access_token, "Can't execute background task for user %s without access_token" % self.fb_uid
            self.fb_graph = facebook.GraphAPI(self.user.fb_access_token)
        else:
            self.fb_graph = facebook.GraphAPI(None)
        self.allow_cache = bool(int(self.request.get('allow_cache', 1)))
        self.batch_lookup = fb_api.CommonBatchLookup(self.fb_uid, self.fb_graph, allow_cache=self.allow_cache)
        return return_value

class TrackNewUserFriendsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        app_friend_list = self.fb_graph.request('fql', args=dict(q=GET_FRIEND_APP_USERS % self.fb_uid))
        logging.info("app_friend_list is %s", app_friend_list)
        user_friends = users.UserFriendsAtSignup.get_or_insert(str(self.fb_uid))
        user_friends.registered_friend_ids = [x['uid'] for x in app_friend_list['data']]
        user_friends.put()
    post=get

class LoadFriendListHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        friend_list_id = self.request.get('friend_list_id')
        self.batch_lookup.lookup_friend_list(friend_list_id)
        self.batch_lookup.finish_loading()
    post=get

class LoadEventHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        db_events = [x for x in eventdata.DBEvent.get_by_key_name(event_ids) if x]
        fb_reloading.load_fb_event(self.batch_lookup, db_events)
    post=get

class LoadEventAttendingHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        db_events = [x for x in eventdata.DBEvent.get_by_key_name(event_ids) if x]
        fb_reloading.load_fb_event_attending(self.batch_lookup, db_events)
    post=get

class LoadUserHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        load_users = users.User.get_by_key_name(user_ids)
        fb_reloading.load_fb_user(self.batch_lookup, load_users[0])
    post=get

class ReloadAllUsersHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        fb_reloading.mr_load_fb_user(self.batch_lookup)
    post=get

class ReloadAllEventsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        fb_reloading.mr_load_fb_event(self.batch_lookup)
        fb_reloading.mr_load_fb_event_attending(self.batch_lookup)
    post=get

class ReloadPastEventsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        fb_reloading.mr_load_past_fb_event(self.batch_lookup)
    post=get

class ReloadFutureEventsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        fb_reloading.mr_load_future_fb_event(self.batch_lookup)
    post=get

class ReloadAllEventsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        fb_reloading.mr_load_all_fb_event(self.batch_lookup)
    post=get

class EmailAllUsersHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        fb_reloading.mr_email_user(self.batch_lookup)
    post=get

class EmailUserHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        load_users = users.User.get_by_key_name(user_ids)
        fb_reloading.email_user(self.batch_lookup, load_users[0])
    post=get

class ComputeRankingsHandler(webapp2.RequestHandler):
    def get(self):
        rankings.begin_ranking_calculations()

class LoadAllPotentialEventsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        fb_reloading.mr_load_potential_events(self.batch_lookup)

class LoadPotentialEventsForFriendsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        friend_lists = []
        #TODO(lambert): extract this out into some sort of dynamic lookup based on Mike Lambert
        friend_lists.append('530448100598') # Freestyle SF
        friend_lists.append('565645040648') # Freestyle NYC
        friend_lists.append('734193578028') # Freestyle Asia
        friend_lists.append('612289903968') # Freestyle LA/SD
        friend_lists.append('646041540418') # Freestyle Europe
        friend_lists.append('583877258138') # Freestyle Elsewhere
        friend_lists.append('565645070588') # Choreo SF
        friend_lists.append('556389713398') # Choreo LA
        friend_lists.append('565645155418') # Choreo Elsewhere
        for x in friend_lists:
            self.batch_lookup.lookup_friend_list(x)
        self.batch_lookup.finish_loading()
        for fl in friend_lists:
            friend_ids = [x['id'] for x in self.batch_lookup.data_for_friend_list(fl)['friend_list']['data']]
            backgrounder.load_potential_events_for_friends(self.fb_uid, friend_ids, allow_cache=self.allow_cache)

class LoadPotentialEventsFromWallPostsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        min_potential_events = self.request.get('min_potential_events')
        thing_scraper.mapreduce_scrape_all_sources(self.batch_lookup, min_potential_events=min_potential_events)

class LoadPotentialEventsForUserHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        fb_reloading.load_potential_events_for_user_ids(self.batch_lookup.copy(), user_ids)

class RecacheSearchIndex(BaseTaskFacebookRequestHandler):
    def get(self):
        search.recache_everything(self.batch_lookup)

class RefreshFulltextSearchIndex(BaseTaskFacebookRequestHandler):
    def get(self):
        index_future = bool(int(self.request.get('index_future', 1)))
        search.construct_fulltext_search_index(self.batch_lookup, index_future=index_future)

class TimingsKeepAlive(BaseTaskRequestHandler):
    def get(self):
        timings.keep_alive()

class TimingsProcessDay(BaseTaskRequestHandler):
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

