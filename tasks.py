
import urllib

import base_servlet
import facebook
from django.utils import simplejson
from google.appengine.ext.webapp import RequestHandler
from events import users

class BaseTaskFacebookRequestHandler(RequestHandler):
    def initialize(self, request, response):
        super(BaseTaskFacebookRequestHandler, self).initialize(request, response)

        self.fb_uid = int(self.request.get('user_id'))
        user = users.get_user(self.fb_uid)
        self.fb_graph = facebook.GraphAPI(user.fb_access_token)

class TrackNewUserFriendsHandler(BaseTaskFacebookRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        app_friend_list = self.fb_graph.request('method/friends.getAppUsers')
        user_friends = users.UserFriendsAtSignup.gql('where fb_uid = :fb_uid', fb_uid=self.fb_uid).fetch(1)[0]
        user_friends.registered_friend_ids = app_friend_list
        user_friends.put()
    post=get

class LoadEventHandler(BaseTaskFacebookRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        batch_lookup = base_servlet.BatchLookup(self.fb_uid, self.fb_graph)
        for event_id in event_ids:
            batch_lookup.lookup_event(event_id)
        batch_lookup.finish_loading()
    post=get

class LoadUserHandler(BaseTaskFacebookRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        batch_lookup = base_servlet.BatchLookup(self.fb_uid, self.fb_graph)
        for user_id in user_ids:
            batch_lookup.lookup_user(user_id)
        batch_lookup.finish_loading()
    post=get
