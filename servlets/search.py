#!/usr/bin/env python

import datetime
import logging
import time

import base_servlet
from events import cities
from events import eventdata
from events import tags
from events import users
from logic import rankings
from logic import friends
from logic import rsvp
from logic import search
import fb_api
import locations

class ResultsHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        tags_set = self.request.get_all('tag')
        start_time = None
        if self.request.get('start_date'):
            start_time = datetime.datetime.strptime(self.request.get('start_date'), '%m/%d/%Y')
        end_time = None
        if self.request.get('end_date'):
            end_time = datetime.datetime.strptime(self.request.get('end_date'), '%m/%d/%Y')
        query = search.SearchQuery(any_tags=tags_set, start_time=start_time, end_time=end_time)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)
        rsvp.decorate_with_rsvps(self.batch_lookup, search_results)

        self.display['results'] = search_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        self.render_template('results')

class RelevantHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        if not self.request.get('location'):
            return True
        return False

    def get(self):
        self.handle()

    def post(self):
        self.handle()

    def handle(self):
        self.finish_preload()
        if self.user and not self.user.location and not self.request.get('ajax'):
            self.user.add_message("We could not retrieve your location from facebook. Please fill out a location below")
            self.redirect('/user/edit')
            return
        city_name = None
        location = None
        distance = None
        distance_units = None
        distance_in_km = None
        latlng_location = None
        if self.request.get('city_name'):
            city_name = self.request.get('city_name')
        else:
            location = self.request.get('location', self.user and self.user.location)
            distance = int(self.request.get('distance', self.user and self.user.distance))
            distance_units = self.request.get('distance_units', self.user and self.user.distance_units)
            if distance_units == 'miles':
                distance_in_km = locations.miles_in_km(distance)
            else:
                distance_in_km = distance
            latlng_location = locations.get_geocoded_location(location)['latlng']
        past = self.request.get('past', '0') not in ['0', '', 'False', 'false']


        min_attendees = int(self.request.get('min_attendees', self.user and self.user.min_attendees or 0))

        dance_type = self.request.get('dance_type', self.user and self.user.dance_type) or users.DANCE_TYPES_LIST[0]['internal']

        self.display['event_types'] = [x['name'] for x in users.DANCE_TYPES_LIST if x['internal'] == dance_type][0].lower()

        self.display['location'] = location
        self.display['defaults'] = {
            'city_name': city_name,
            'distance': distance,
            'distance_units': distance_units,
            'location': location,
            'dance_type': dance_type,
            'min_attendees': min_attendees,
            'past': past,
        }
        
        if past:
            time_period = tags.TIME_PAST
        else:
            time_period = tags.TIME_FUTURE

        self.display['DANCE_TYPES_LIST'] = users.DANCE_TYPES_LIST

        query = search.SearchQuery(time_period=time_period, city_name=city_name, location=latlng_location, distance_in_km=distance_in_km, dance_type=dance_type, min_attendees=min_attendees)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)
        # We can probably speed this up 2x by shrinking the size of the fb-event-attending objects. a list of {u'id': u'100001860311009', u'name': u'Dance InMinistry', u'rsvp_status': u'attending'} is 50% overkill.
        a = time.time()
        friends.decorate_with_friends(self.batch_lookup, search_results)
        logging.info("Decorating with friends-attending took %s seconds", time.time() - a)
        a = time.time()
        rsvp.decorate_with_rsvps(self.batch_lookup, search_results)
        logging.info("Decorating with personal rsvp data took %s seconds", time.time() - a)

        past_results, present_results, grouped_results = search.group_results(search_results)
        if time_period == tags.TIME_FUTURE:
            present_results = past_results + present_results
            past_results = []

        a = time.time()
        closest_cityname = cities.get_largest_nearby_city_name(location)
        #TODO(lambert): perhaps produce optimized versions of these without styles/times, for use on the homepage? less pickling/loading required
        event_top_n_cities, event_selected_n_cities = rankings.top_n_with_selected(rankings.get_thing_ranking(rankings.get_city_by_event_rankings(), rankings.ANY_STYLE, rankings.ALL_TIME), closest_cityname)
        user_top_n_cities, user_selected_n_cities = rankings.top_n_with_selected(rankings.get_thing_ranking(rankings.get_city_by_user_rankings(), rankings.DANCE_DANCER, rankings.ALL_TIME), closest_cityname)
        logging.info("Computing current city and top-N cities took %s seconds", time.time() - a)

        self.display['current_city'] = closest_cityname
        self.display['user_top_n_cities'] = user_top_n_cities
        self.display['event_top_n_cities'] = event_top_n_cities
        self.display['user_selected_n_cities'] = user_selected_n_cities
        self.display['event_selected_n_cities'] = event_selected_n_cities

        self.display['past_view_url'] = '/events/relevant?ajax=1&past=1&%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())
        self.display['calendar_view_url'] = '/calendar?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())

        self.display['num_upcoming_results'] = sum([len(x.results) for x in grouped_results])
        self.display['past_results'] = past_results
        self.display['ongoing_results'] = present_results
        self.display['grouped_upcoming_results'] = grouped_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        if self.request.get('ajax'):
            #TODO(lambert): do we want this to handle include_description=True or not based on from /city or /?...
            self.render_template('results_ajax')
        else:
            self.render_template('results')

