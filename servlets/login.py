#!/usr/bin/env python

import datetime
import logging
import urllib

import base_servlet
from events import users
from google.appengine.api import taskqueue

from logic import backgrounder
from logic import rankings
from logic import search_base

def get_location(fb_user):
    if fb_user['profile'].get('location'):
        facebook_location = fb_user['profile']['location']['name']
    else:
        facebook_location = None
    return facebook_location

class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def is_login_page(self):
        return True

    #TODO(lambert): move this into the same base / handler, so we don't do stupid redirects to /login
    def get(self, needs_city=False):
        next = self.request.get('next') or '/'

        want_specific_page = (next != '/?')
        if want_specific_page:
            #TODO(lambert): do a much better job here, either not requiring login for more pages, or supporting logged-out error messages too.
            self.display['errors'] = ['Sorry, but you must Log In to view that page.']

        # If they're logged in, and have an account created, update and redirect
        if self.fb_uid:
            user = users.User.get_by_key_name(str(self.fb_uid))
            if user and not user.expired_oauth_token:
                self.redirect(next)
                return

        # Treat them like a totally logged-out user since they have no user object yet
        self.fb_uid = None

        # Explicitly do not preload anything from facebook for this servlet
        # self.finish_preload()

        self.display['user_message'] = self.get_cookie('User-Message')

        city_rankings = rankings.get_thing_ranking(rankings.get_city_by_event_rankings(), rankings.LAST_MONTH)
        top_na_rankings = [x for x in city_rankings if 'United States' in x['key'] or 'Canada' in x['key'] or 'Mexico' in x['key']][:20]
        self.display['top_cities'] = [(x['key'], x['key'].split(', ')[0]) for x in top_na_rankings]
        self.display['top_european_countries'] = ['Czech Republic', 'Finland', 'France', 'Germany', 'Ireland', 'Italy', 'Norway', 'Poland', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom', 'Portugal']
        self.display['top_continents'] = ['Asia', 'Africa', 'Australia', 'South America']

        self.display['defaults'] = search_base.FrontendSearchQuery()
        self.display['defaults'].location = self.request.get('location')
        self.display['defaults'].keywords = self.request.get('keywords')
        self.display['defaults'].deb = self.request.get('deb')

        self.display['next'] = next
        logging.info(self.display['next'])
        self.display['needs_city'] = needs_city
        self.render_template('login')

def construct_user(fb_uid, access_token, access_token_expires, fb_user, request, referer):
        next = request.get('next') or '/'
        user = users.User.get_by_key_name(str(fb_uid))
        if user:
            logging.info("Already have user with name %s, passing through to %s", user.full_name, next)
            return

        # If they're a new-user signup, but didn't fill out a city and facebook doesn't have a city,
        # then render the get() up above but with an error message to fill out the city
        city = request.get('city') or get_location(fb_user)
        logging.info("User passed in a city of %r, facebook city is %s", request.get('city'), get_location(fb_user))
        if not city:
            logging.info("Signup User forgot their city, so require that now.")
            #TODO(lambert): FIXME!!!
            #get(needs_city=True)
            #return

        user = users.User(key_name=str(fb_uid))
        user.fb_access_token = access_token
        user.fb_access_token_expires = access_token_expires
        user.location = city
        # grab the cookie to figure out who referred this user
        logging.info("Referer was: %s", referer)
        if referer:
            user.inviting_fb_uid = int(referer)

        user.send_email = True
        user.distance = '50'
        user.distance_units = 'miles'
        user.min_attendees = 0

        user.creation_time = datetime.datetime.now()

        user.login_count = 1
        user.last_login_time = user.creation_time

        user.compute_derived_properties(fb_user)
        logging.info("Saving user with name %s", user.full_name)
        user.put()

        logging.info("Requesting background load of user's friends")
        # Must occur after User is put with fb_access_token
        taskqueue.add(method='GET', url='/tasks/track_newuser_friends?' + urllib.urlencode({'user_id': fb_uid}), queue_name='slow-queue')
        # Now load their potential events, to make "add event page" faster
        backgrounder.load_potential_events_for_users([fb_uid])
