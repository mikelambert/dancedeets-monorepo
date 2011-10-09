
import cgi
import datetime
import logging
import re
import time
import urllib
import urlparse

from django.utils import simplejson
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import RequestHandler
from google.appengine.runtime import apiproxy_errors


import base_servlet
from events import eventdata
from events import users
import facebook
import fb_api
from logic import backgrounder
from logic import email_events
from logic import potential_events
from logic import rankings
from logic import search
from logic import thing_db
from logic import thing_scraper

# How long to wait before retrying on a failure. Intended to prevent hammering the server.
RETRY_ON_FAIL_DELAY = 60

class BaseTaskRequestHandler(RequestHandler):
    def requires_login(self):
        return False


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
        app_friend_list = self.fb_graph.api_request('method/friends.getAppUsers')
        user_friends = users.UserFriendsAtSignup.get_or_insert(str(self.fb_uid))
        user_friends.registered_friend_ids = app_friend_list
        user_friends.put()
    post=get

class LoadEventHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        for event_id in event_ids:
            self.batch_lookup.lookup_event(event_id)
        self.batch_lookup.finish_loading()
        db_events = eventdata.DBEvent.get_by_key_name(event_ids)
        failed_fb_event_ids = []
        for event_id, db_event in zip(event_ids, db_events):
            if not db_event:
                continue # could be due to uncache-able events that we don't save here
            try:
                fb_event = self.batch_lookup.data_for_event(db_event.fb_event_id)
                db_event.make_findable_for(fb_event)
                db_event.put()
            except:
                logging.exception("Error loading event, going to retry eid=%s", event_id)
                failed_fb_event_ids.append(event_id)
        backgrounder.load_events(failed_fb_event_ids, self.allow_cache, countdown=RETRY_ON_FAIL_DELAY)
    post=get

class LoadEventAttendingHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        for event_id in event_ids:
            self.batch_lookup.lookup_event_attending(event_id)
        self.batch_lookup.finish_loading()
        db_events = eventdata.DBEvent.get_by_key_name(event_ids)
        failed_fb_event_ids = []
        for event_id, db_event in zip(event_ids, db_events):
            if not db_event:
                continue # could be due to uncache-able events that we don't save here
            try:
                event_attending = self.batch_lookup.data_for_event_attending(event_id)
                db_event.include_attending_summary(event_attending)
                db_event.put()
            except:
                logging.exception("Error loading event, going to retry eid=%s", event_id)
                failed_fb_event_ids.append(event_id)
        backgrounder.load_event_attending(failed_fb_event_ids, self.allow_cache, countdown=RETRY_ON_FAIL_DELAY)
    post=get

class LoadFriendListHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        friend_list_id = self.request.get('friend_list_id')
        self.batch_lookup.lookup_friend_list(friend_list_id)
        self.batch_lookup.finish_loading()
    post=get

class LoadUserHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        assert len(user_ids) == 1
        user_id = user_ids[0]
        self.batch_lookup.lookup_user(user_id)
        try:
            self.batch_lookup.finish_loading()
        except fb_api.ExpiredOAuthToken:
            logging.info("Auth token now expired, mark as such.")
            user = users.User.get_by_key_name(user_id)
            user.expired_oauth_token = True
            user.put()
            return

        try:
            self.batch_lookup.data_for_user(user_id)
        except:
            logging.exception("Error loading user, going to retry uid=%s", user_id)
            backgrounder.load_users([user_id], self.allow_cache, countdown=RETRY_ON_FAIL_DELAY)
            return

        user = users.User.get_by_key_name(user_id)
        user.compute_derived_properties(self.batch_lookup.data_for_user(user_id))
        user.put()
        backgrounder.load_potential_events_for_users([user_id], allow_cache=False)
    post=get

class ReloadAllUsersHandler(BaseTaskRequestHandler):
    def get(self):
        user_ids = [user.fb_uid for user in users.User.all() if not user.expired_oauth_token]
        backgrounder.load_users(user_ids, allow_cache=False)    
    post=get

class ResaveAllUsersHandler(BaseTaskRequestHandler):
    def get(self):
        user_ids = [user.fb_uid for user in users.User.all()]
        backgrounder.load_users(user_ids)
    post=get

class ResaveAllEventsHandler(BaseTaskRequestHandler):
    def get(self):
        db_events = eventdata.DBEvent.all()
        event_ids = [db_event.fb_event_id for db_event in db_events if db_event.tags != []]
        for db_event in db_events:
            if db_event.tags == []:
                logging.info("Deleting db_event id %s", db_event.fb_event_id)
                db_event.delete()
        backgrounder.load_events_full(event_ids)
    post=get

class ReloadAllEventsHandler(BaseTaskRequestHandler):
    def get(self):
        event_ids = [db_event.fb_event_id for db_event in eventdata.DBEvent.all()]
        logging.info("Found %s total events to reload", len(event_ids))
        backgrounder.load_events_full(event_ids, allow_cache=False)
    post=get

class ReloadPastEventsHandler(BaseTaskRequestHandler):
    def get(self):
        event_ids = [db_event.fb_event_id for db_event in eventdata.DBEvent.gql("WHERE search_time_period = :1", eventdata.TIME_PAST)]
        logging.info("Found %s past events to reload", len(event_ids))
        backgrounder.load_events_full(event_ids, allow_cache=False)
    post=get

class ReloadFutureEventsHandler(BaseTaskRequestHandler):
    def get(self):
        event_ids = [db_event.fb_event_id for db_event in eventdata.DBEvent.gql('WHERE search_time_period = :1', eventdata.TIME_FUTURE)]
        logging.info("Found %s future events to reload", len(event_ids))
        backgrounder.load_events_full(event_ids, allow_cache=False)    
    post=get

class EmailAllUsersHandler(BaseTaskRequestHandler):
    def get(self):
        user_ids = [user.fb_uid for user in users.User.all()]
        backgrounder.email_users(user_ids)    
    post=get

class EmailUserHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        self.batch_lookup.lookup_user(self.user.fb_uid)
        self.batch_lookup.lookup_user_events(self.user.fb_uid)
        self.batch_lookup.finish_loading()
        should_send = not self.request.get('no_send')
        message = email_events.email_for_user(self.user, self.batch_lookup, self.fb_graph, should_send=should_send)
        if message:
            self.response.out.write(message.html)
    post=get

class CleanupWorkHandler(RequestHandler):
    def get(self):
        event_ids = [db_event.fb_event_id for db_event in eventdata.DBEvent.gql("WHERE address = null and start_time != null")]
        if event_ids:
            event_urls = ['http://www.dancedeets.com/events/admin_edit?event_id=%s' % x for x in event_ids]
            html = "Events missing addresses:\n\n" + "\n".join(event_urls)
            message = mail.EmailMessage(
                sender="events@dancedeets.com",
                to="mlambert@gmail.com",
                subject="Events missing addresses",
                html=html
            )

class ComputeRankingsHandler(RequestHandler):
    def get(self):
        rankings.begin_ranking_calculations()

class LoadAllPotentialEventsHandler(RequestHandler):
    #OPT: maybe some day make this happen immediately after reloading users, so we can guarantee the latest users' state, rather than adding another day to the pipeline delay
    #TODO(lambert): email me when we get the latest batch of things completed.
    def get(self):
        user_ids = [user.fb_uid for user in users.User.all() if not user.expired_oauth_token]
        # must load from cache here, since we don't load it as part of user lookups anymore
        backgrounder.load_potential_events_for_users(user_ids, allow_cache=False)

class LoadPotentialEventsForFriendsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        friend_lists = []
        #TODO(lambert): extract this out into some sort of dynamic lookup based on Mike Lambert
        friend_lists.append('530448100598') # Freestyle SF
        friend_lists.append('565645070588') # Choreo SF
        friend_lists.append('565645040648') # Freestyle NYC
        friend_lists.append('556389713398') # Choreo LA
        friend_lists.append('583877258138') # Freestyle Elsewhere
        friend_lists.append('565645155418') # Choreo Elsewhere
        for x in friend_lists:
            self.batch_lookup.lookup_friend_list(x)
        self.batch_lookup.finish_loading()
        for fl in friend_lists:
            friend_ids = [x['id'] for x in self.batch_lookup.data_for_friend_list(fl)['friend_list']['data']]
            backgrounder.load_potential_events_for_friends(self.fb_uid, friend_ids, allow_cache=self.allow_cache)

class LoadPotentialEventsFromWallPostsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        thing_scraper.mapreduce_scrape_all_sources(self.batch_lookup)
        return

""" Old id-loading code
        filemap = [
            'choreo_ids.txt',
            'freestyle_ids.txt',
            'dance_ids.txt',
        ]
        for filename in filemap:
            # ignore style_type
            lines = open('dance_keywords/%s' % filename).readlines()
            friendpage_ids = [re.sub('[ #].*\n|\n', '', x) for x in lines]
            friendpage_ids = [x.replace('.', '') for x in friendpage_ids]
            batch_lookup = self.batch_lookup.copy()
            for friend_id in friendpage_ids:
                batch_lookup.lookup_thing_feed(friend_id)
            batch_lookup.finish_loading()

            for friend_id in friendpage_ids:
                try:
                    data = batch_lookup.data_for_thing_feed(friend_id)
                except fb_api.NoFetchedDataException:
                    continue
                thing_db.create_source_for_id(friend_id, data)

            #sources from ids...
            #thing_scraper.scrape_events_from_sources(self.batch_lookup, friendpage_ids)
"""

class LoadPotentialEventsForUserHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        if self.user.expired_oauth_token:
            return
        for user_id in user_ids:
            self.batch_lookup.lookup_user_events(user_id)
        self.batch_lookup.finish_loading()
        for user_id in user_ids:
            potential_events.get_potential_dance_events(self.batch_lookup, user_id)

class UpdateLastLoginTimeHandler(RequestHandler):
    def get(self):
        user = users.User.get_by_key_name(self.request.get('user_id'))
        user.last_login_time = datetime.datetime.now()
        if getattr(user, 'login_count'):
            user.login_count += 1
        else:
            user.login_count = 2 # once for this one, once for initial creation
        try:
            user.put()
        except apiproxy_errors.CapabilityDisabledError:
            pass # read-only mode!

class RecacheSearchIndex(BaseTaskFacebookRequestHandler):
    def get(self):
        search.recache_everything(self.batch_lookup)

