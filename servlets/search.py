#!/usr/bin/env python

import datetime
import logging

import base_servlet
from events import cities
from events import eventdata
from events import tags
from events import users
from logic import rsvp
from logic import search
import fb_api
import locations

class SearchHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        self.display['freestyle_types'] = tags.FREESTYLE_EVENT_LIST
        self.display['choreo_types'] = tags.CHOREO_EVENT_LIST
        self.display['styles'] = tags.STYLES

        self.display['cities'] = []
        self.render_template('search')

class ResultsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        tags_set = self.request.get_all('tag')
        start_time = None
        if self.request.get('start_date'):
            start_time = datetime.datetime.strptime(self.request.get('start_date'), '%m/%d/%Y')
        end_time = None
        if self.request.get('end_date'):
            end_time = datetime.datetime.strptime(self.request.get('end_date'), '%m/%d/%Y')
        query = search.SearchQuery(self.parse_fb_timestamp, any_tags=tags_set, start_time=start_time, end_time=end_time)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)
        rsvp.decorate_with_rsvps(self.batch_lookup, search_results)

        self.display['results'] = search_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        self.render_template('results')

class RelevantHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        if not self.user.location:
            #TODO(lambert): use a redirect message here!
            self.redirect('/user/edit')
            return
        user_location = self.request.get('user_location', self.user.location)
        distance = int(self.request.get('distance', self.user.distance))
        distance_units = self.request.get('distance_units', self.user.distance_units)
        if distance_units == 'miles':
            distance_in_km = locations.miles_in_km(distance)
        else:
            distance_in_km = distance
        freestyle = self.request.get('freestyle', self.user.freestyle)
        choreo = self.request.get('choreo', self.user.choreo)

        self.display['user_location'] = user_location
        self.display['defaults'] = {
            'distance': distance,
            'distance_units': distance_units,
            'user_location': user_location,
            'freestyle': freestyle,
            'choreo': choreo,
        }
        
        self.display['DANCES'] = users.DANCES
        self.display['DANCE_HEADERS'] = users.DANCE_HEADERS
        self.display['DANCE_LISTS'] = users.DANCE_LISTS

        latlng_user_location = locations.get_geocoded_location(user_location)['latlng']
        query = search.SearchQuery(self.parse_fb_timestamp, time_period=tags.TIME_FUTURE, location=latlng_user_location, distance_in_km=distance_in_km, freestyle=freestyle, choreo=choreo)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)
        rsvp.decorate_with_rsvps(self.batch_lookup, search_results)

        self.display['results'] = search_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        self.render_template('results')

