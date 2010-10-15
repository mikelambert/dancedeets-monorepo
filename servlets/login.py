#!/usr/bin/env python

import datetime
import logging
import urllib

import base_servlet
from events import tags
from events import users
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

import locations
from logic import rankings

class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        next = self.request.get('next') or '/'

        self.display['attempt_autologin'] = 1
        # If they're logged in, and have an account created, update and redirect
        if self.fb_uid:
            user = users.User.get_by_key_name(str(self.fb_uid))
            if user:
                # We need to load the user info
                user.fb_access_token = self.fb_graph.access_token
                user.put()
                self.redirect(next)
                return 
            else:
                # Do not attempt auto-login because we don't have a User on our side.
                # Let the client sit there and wait for the user to manually sign up.
                self.display['attempt_autologin'] = 0

        # Treat them like a totally logged-out user since they have no user object yet
        self.fb_uid = None

        # Explicitly do not preload anything from facebook for this servlet
        # self.finish_preload()

        #TODO(lambert): save off totals somewhere, perhaps in a separate mapreduce, so that these bigger blobs don't need to be loaded
        event_rankings = rankings.get_city_by_event_rankings()
        if event_rankings:
            total_events = rankings.compute_sum(event_rankings, [rankings.ANY_STYLE], rankings.ALL_TIME)
        else:
            total_events = 0
        user_rankings = rankings.get_city_by_user_rankings()
        if user_rankings:
            total_users = rankings.compute_sum(user_rankings, [rankings.DANCE_FAN], rankings.ALL_TIME)
        else:
            total_users = 0
        self.display['total_events'] = total_events
        self.display['total_users'] = total_users

        self.display['freestyle_types'] = [x[1] for x in tags.FREESTYLE_EVENT_LIST]
        self.display['choreo_types'] = [x[1] for x in tags.CHOREO_EVENT_LIST]

        self.display['next'] = '/login?%s' % urllib.urlencode({'next': next})
        self.render_template('login')

    def post(self):
        assert self.fb_uid

        self.finish_preload()
        next = self.request.get('next') or '/'
        user = users.User.get_by_key_name(str(self.fb_uid))
        if user:
            self.redirect(next)
            
        user = users.User(key_name=str(self.fb_uid))
        user.location = self.request.get('city')
        user_type = self.request.get('user_type')
        if user_type == 'fan':
            user.freestyle = users.FREESTYLE_FAN
            user.choreo = users.CHOREO_FAN
        elif user_type == 'choreo':
            user.freestyle = users.FREESTYLE_FAN
            user.choreo = users.CHOREO_DANCER
        elif user_type == 'freestyle':
            user.freestyle = users.FREESTYLE_DANCER
            user.choreo = users.CHOREO_FAN
        elif user_type == 'everything':
            user.freestyle = users.FREESTYLE_DANCER
            user.choreo = users.CHOREO_DANCER
        else:
            self.add_error("Unknown user_type: %s" % user_type)
    
        self.errors_are_fatal()

        user.send_email = True
        if not user.location_country or user.location_country in locations.MILES_COUNTRIES:
            user.distance = '90'
            user.distance_units = 'miles'
        else:
            user.distance = '150'
            user.distance_units = 'km'
        user.creation_time = datetime.datetime.now()

        user_friends = users.UserFriendsAtSignup(key_name=str(self.fb_uid))
        user_friends.put()
        taskqueue.add(method='GET', url='/tasks/track_newuser_friends?' + urllib.urlencode({'user_id': self.fb_uid}))

        user.compute_derived_properties(self.batch_lookup.data_for_user(self.fb_uid))
        user.put()

        self.redirect(next)
