#!/usr/bin/env python

import datetime
import logging
import urllib

import base_servlet
from events import eventdata
from events import users
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

import locations
from logic import backgrounder
from logic import rankings
from logic import search

def get_location(fb_user):
    if fb_user['profile'].get('location'):
        facebook_location = fb_user['profile']['location']['name']
    else:
        facebook_location = None
    return facebook_location

class LoginHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def newpage(self):
        query = search.SearchQuery(time_period=eventdata.TIME_FUTURE, location=(0,0), distance_in_km=locations.miles_in_km(12000), min_attendees=500)
        # self.fb_uid should be None for these logged out users...
                search_results = query.get_search_results(self.fb_uid, self.fb_graph)
        past_results, present_results, grouped_results = search.group_results(search_results)
        # Need to reverse engineer our search query terms to generate these URLs
                self.display['past_view_url'] = '/events/relevant?ajax=1&past=1&%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())
                self.display['calendar_view_url'] = '/calendar?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())
                self.display['past_results'] = past_results
                self.display['ongoing_results'] = present_results
                self.display['grouped_upcoming_results'] = grouped_results

        # Need to generate a display-defaults dict that's preselected as best as we can for the user, along with clientside code to figure out their location as best we can.

        self.display['defaults'] = {
            'city_name': '',
            'distance': 100,
            'distance_units': 'miles',
            'location': 'New York, NY',
            'min_attendees': 0,
            'past': False,
        }

        self.render_template('results')


    def get(self, needs_city=False):
        next = self.request.get('next') or '/'

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

        if self.request.get('newpage'):
            return self.newpage()

        self.display['user_message'] = self.get_cookie('User-Message')

        city_rankings = rankings.get_thing_ranking(rankings.get_city_by_event_rankings(), rankings.ALL_TIME)
        top_na_rankings = [x for x in city_rankings if 'United States' in x['key'] or 'Canada' in x['key'] or 'Mexico' in x['key']][:10]
        self.display['top_cities'] = [(x['key'], x['key'].split(', ')[0]) for x in top_na_rankings]
        self.display['top_continents'] = [
            ('paris', 'Europe'),
            ('beijing', 'Asia'),
            ('sydney', 'Australia'),
            ('sao paolo', 'South America'),
        ]

                self.display['defaults'] = {
                        'city_name': '',
                        'distance': '100',
                        'distance_units': 'miles',
                        'location': '', # maybe set via ajax
                        'min_attendees': 0,
                        'past': False,
                }


        self.display['next'] = next
        logging.info(self.display['next'])
        self.display['needs_city'] = needs_city
        self.render_template('login')

    def post(self):
        logging.info("Login Post with fb_uid = %s", self.fb_uid)
        assert self.fb_uid
        self.batch_lookup.lookup_user(self.fb_uid, allow_cache=False)
        self.finish_preload()
        fb_user = self.batch_lookup.data_for_user(self.fb_uid)
        next = self.request.get('next') or '/'
        user = users.User.get_by_key_name(str(self.fb_uid))
        if user:
            logging.info("Already have user with name %s, passing through to %s", user.full_name, next)
            self.redirect(next)
            return

        # If they're a new-user signup, but didn't fill out a city and facebook doesn't have a city,
        # then render the get() up above but with an error message to fill out the city
        city = self.request.get('city') or get_location(fb_user)
        logging.info("User passed in a city of %r, facebook city is %s", self.request.get('city'), get_location(fb_user))
        if not city:
            logging.info("Signup User forgot their city, so require that now.")
            self.get(needs_city=True)
            return

        user = users.User(key_name=str(self.fb_uid))
        user.fb_access_token = self.fb_graph.access_token
        user.location = city
        # grab the cookie to figure out who referred this user
        referer = self.get_cookie('User-Referer')
        logging.info("Referer was: %s", referer)
        if referer:
            user.inviting_fb_uid = int(referer)
        self.errors_are_fatal()

        user.send_email = True
        user.distance = '100'
        user.distance_units = 'miles'
        user.creation_time = datetime.datetime.now()

        user.compute_derived_properties(fb_user)
        logging.info("Saving user with name %s", user.full_name)
        user.put()

        logging.info("Requesting background load of user's friends")
        # Must occur after User is put with fb_access_token
        taskqueue.add(method='GET', url='/tasks/track_newuser_friends?' + urllib.urlencode({'user_id': self.fb_uid}))
        # Now load their potential events, to make "add event page" faster
        backgrounder.load_potential_events_for_users([self.fb_uid])

        logging.info("Redirecting to %s", next)
        self.redirect(next)
