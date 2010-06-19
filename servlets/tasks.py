
import datetime
import logging
import time
import urllib

from django.utils import simplejson
from google.appengine.ext.webapp import RequestHandler

from events import eventdata
from events import users
from logic import backgrounder
import facebook
import fb_api

class BaseTaskRequestHandler(RequestHandler):
  def requires_login(self):
    return False


class BaseTaskFacebookRequestHandler(BaseTaskRequestHandler):
    def requires_login(self):
        return False

    def initialize(self, request, response):
        return_value = super(BaseTaskFacebookRequestHandler, self).initialize(request, response)

        self.fb_uid = int(self.request.get('user_id'))
        self.user = users.User.get(self.fb_uid)
        assert self.user.fb_access_token, "Can't execute background task for user %s without access_token" % self.fb_uid
        self.fb_graph = facebook.GraphAPI(self.user.fb_access_token)
        self.allow_cache = bool(int(self.request.get('allow_cache', 1)))
        self.batch_lookup = fb_api.BatchLookup(self.fb_uid, self.fb_graph, allow_cache=self.allow_cache)
        return return_value

class TrackNewUserFriendsHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        app_friend_list = self.fb_graph.api_request('method/friends.getAppUsers')
        user_friends = users.UserFriendsAtSignup.gql('where fb_uid = :fb_uid', fb_uid=self.fb_uid).fetch(1)[0]
        user_friends.registered_friend_ids = app_friend_list
        user_friends.put()
    post=get

class LoadEventHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [int(x) for x in self.request.get('event_ids').split(',') if x]
        for event_id in event_ids:
            self.batch_lookup.lookup_event(event_id)
        self.batch_lookup.finish_loading()
        db_events = eventdata.get_db_events(event_ids)
        failed_fb_event_ids = []
        for db_event in db_events:
            try:
                fb_event = self.batch_lookup.data_for_event(db_event.fb_event_id)
            except KeyError:
                failed_fb_event_ids.append(db_event.fb_event_id)
            else:
                db_event.make_findable_for(fb_event)
                db_event.put()
        backgrounder.load_events(failed_fb_event_ids, self.allow_cache)
    post=get

class LoadEventMembersHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        event_ids = [int(x) for x in self.request.get('event_ids').split(',') if x]
        for event_id in event_ids:
            self.batch_lookup.lookup_event_members(event_id)
        self.batch_lookup.finish_loading()
    post=get

class LoadUserHandler(BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [int(x) for x in self.request.get('user_ids').split(',') if x]
        for user_id in user_ids:
            self.batch_lookup.lookup_user(user_id)
        self.batch_lookup.finish_loading()
    post=get

class ReloadAllEventsHandler(BaseTaskRequestHandler):
    def get(self):
        event_ids = [db_event.fb_event_id for db_event in eventdata.DBEvent.all()]
        backgrounder.load_events(event_ids)    
    post=get

class ReloadPastEventsHandler(BaseTaskRequestHandler):
    def get(self):
        gm_today = datetime.datetime(*time.gmtime(time.time())[:6])
        event_ids = [db_event.fb_event_id for db_event in eventdata.DBEvent.gql("WHERE end_time < :1", gm_today)]
        backgrounder.load_events(event_ids, allow_cache=False)
    post=get

class ReloadFutureEventsHandler(BaseTaskRequestHandler):
    def get(self):
        gm_yesterday = datetime.datetime(*time.gmtime(time.time())[:6]) - datetime.timedelta(days=1)
        event_ids = [db_event.fb_event_id for db_event in eventdata.DBEvent.gql('WHERE start_time > :1', gm_yesterday)]
        backgrounder.load_events(event_ids, allow_cache=False)    
    post=get

