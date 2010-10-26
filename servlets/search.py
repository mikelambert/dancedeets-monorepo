#!/usr/bin/env python

import datetime
import logging

import base_servlet
from events import cities
from events import eventdata
from events import tags
from events import users
from logic import rankings
from logic import rsvp
from logic import search
import fb_api
import locations

class SearchHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        self.display['freestyle_types'] = tags.FREESTYLE_EVENT_LIST
        self.display['choreo_types'] = tags.CHOREO_EVENT_LIST
        self.display['styles'] = tags.STYLES

        self.display['cities'] = []
        self.render_template('search')

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
        if not self.user:
            # If they're not logged in, require a full set of fields...
            required_fields = ['user_location', 'distance', 'distance_units', 'freestyle', 'choreo']
            for field in required_fields:
                if not self.request.get(field):
                    return True
        return False

    def get(self):
        self.handle()

    def post(self):
        self.handle()

    def handle(self):
        self.finish_preload()
        if self.user and not self.user.location:
            self.user.add_message("We could not retrieve your location from facebook. Please fill out a location below")
            self.redirect('/user/edit')
            return
        user_location = self.request.get('user_location', self.user and self.user.location)
        distance = int(self.request.get('distance', self.user and self.user.distance))
        distance_units = self.request.get('distance_units', self.user and self.user.distance_units)
        if distance_units == 'miles':
            distance_in_km = locations.miles_in_km(distance)
        else:
            distance_in_km = distance
        freestyle = self.request.get('freestyle', self.user and self.user.freestyle)
        choreo = self.request.get('choreo', self.user and self.user.choreo)
        past = self.request.get('past', '0') not in ['0', '', 'False', 'false']

        event_types = []
        if choreo in [x['internal'] for x in users.CHOREO_LIST[1:]]:
            event_types.append('choreo')
        if freestyle in [x['internal'] for x in users.FREESTYLE_LIST[1:]]:
            event_types.append('freestyle')
        self.display['event_types'] = ' and '.join(event_types)

        self.display['user_location'] = user_location
        self.display['defaults'] = {
            'distance': distance,
            'distance_units': distance_units,
            'user_location': user_location,
            'freestyle': freestyle,
            'choreo': choreo,
            'past': past,
        }
        
        self.display['DANCES'] = users.DANCES
        self.display['DANCE_HEADERS'] = users.DANCE_HEADERS
        self.display['DANCE_LISTS'] = users.DANCE_LISTS

        latlng_user_location = locations.get_geocoded_location(user_location)['latlng']
        if past:
            time_period = tags.TIME_PAST
        else:
            time_period = tags.TIME_FUTURE
        query = search.SearchQuery(time_period=time_period, location=latlng_user_location, distance_in_km=distance_in_km, freestyle=freestyle, choreo=choreo)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)
        rsvp.decorate_with_rsvps(self.batch_lookup, search_results)
        past_results, present_results, grouped_results = search.group_results(search_results, past=past)

        closest_cityname = cities.get_closest_city(user_location)
        #TODO(lambert): perhaps produce optimized versions of these without styles/times, for use on the homepage? less pickling/loading required
        event_top_n_cities, event_selected_n_cities = rankings.top_n_with_selected(rankings.get_city_by_event_rankings(), rankings.ANY_STYLE, rankings.ALL_TIME, closest_cityname)
        user_top_n_cities, user_selected_n_cities = rankings.top_n_with_selected(rankings.get_city_by_user_rankings(), rankings.DANCE_DANCER, rankings.ALL_TIME, closest_cityname)
        event_top_n_users, event_selected_n_users = rankings.top_n_with_selected(rankings.get_user_by_event_rankings(city=closest_cityname), rankings.ANY_STYLE, rankings.ALL_TIME, self.fb_uid)
        user_top_n_users, user_selected_n_users = rankings.top_n_with_selected(rankings.get_user_by_user_rankings(city=closest_cityname), rankings.DANCE_DANCER, rankings.ALL_TIME, self.fb_uid)

        user_lists = [user_top_n_users, user_selected_n_users, event_top_n_users, event_selected_n_users]

        all_keys = set()
        for lst in user_lists:
            all_keys.update(d['key'] for (i, sel, d) in lst)

        #TODO(lambert): Use users in memcache? And/or stick this in a per-use cache?
        user_lookup = dict((x.key().name(), x) for x in users.User.get_by_key_name(list(all_keys)) if x)

        for lst in user_lists:
            for i, sel, d in lst:
                if d['key'] in user_lookup:
                    d['key'] = user_lookup[d['key']].full_name
                else:
                    d['key'] = 'Unknown'

        self.display['current_city'] = closest_cityname
        self.display['user_top_n_cities'] = user_top_n_cities
        self.display['event_top_n_cities'] = event_top_n_cities
        self.display['user_selected_n_cities'] = user_selected_n_cities
        self.display['event_selected_n_cities'] = event_selected_n_cities
        self.display['user_top_n_users'] = user_top_n_users
        self.display['event_top_n_users'] = event_top_n_users
        self.display['user_selected_n_users'] = user_selected_n_users
        self.display['event_selected_n_users'] = event_selected_n_users

        self.display['past_view_url'] = '/events/relevant?ajax=1&past=1&%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())
        self.display['calendar_view_url'] = '/calendar?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())

        self.display['past_results'] = past_results
        self.display['ongoing_results'] = present_results
        self.display['grouped_upcoming_results'] = grouped_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        if self.request.get('ajax'):
            self.render_template('results_ajax')
        else:
            self.render_template('results')

