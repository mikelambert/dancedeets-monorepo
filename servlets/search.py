#!/usr/bin/env python

import datetime

import base_servlet
from events import cities
from events import eventdata
from events import tags
from events import users
from logic import rsvp
import fb_api
import locations

class SearchResult(object):
    def __init__(self, fb_user_id, db_event, fb_event, search_query):
        self.fb_user_id = fb_user_id
        self.db_event = db_event
        self.fb_event = fb_event
        self.search_query = search_query
        self.start_time = search_query.parse_fb_timestamp(self.fb_event['info']['start_time'])
        self.end_time = search_query.parse_fb_timestamp(self.fb_event['info']['end_time'])
        self.rsvp_status = "unknown"

    def get_image(self):
        return eventdata.get_event_image_url(self.fb_event['picture'], eventdata.EVENT_IMAGE_MEDIUM)

    def get_attendance(self):
        if self.rsvp_status == 'unsure':
            return 'maybe'
        return self.rsvp_status

class SearchQuery(object):
    MATCH_TAGS = 'TAGS'
    MATCH_TIME = 'TIME'
    MATCH_LOCATION = 'LOCATION'
    MATCH_QUERY = 'QUERY'

    def __init__(self, parse_fb_timestamp, any_tags=None, choreo_freestyle=None, time_period=None, start_time=None, end_time=None, location=None, distance_in_km=None, query_args=None):
        self.parse_fb_timestamp = parse_fb_timestamp
        self.any_tags = set(any_tags or [])
        self.choreo_freestyle = choreo_freestyle
        self.time_period = time_period
        self.start_time = start_time
        self.end_time = end_time
        if self.start_time and self.end_time:
            assert self.start_time < self.end_time
        if self.time_period == tags.TIME_FUTURE and self.end_time:
                assert self.end_time > datetime.datetime.today()
        if self.time_period == tags.TIME_FUTURE and self.start_time:
                assert self.start_time < datetime.datetime.today()
        self.search_regions = None
        self.location = location
        self.distance_in_km = distance_in_km
        self.query_args = query_args

    def matches_event(self, event, fb_event):
        if self.any_tags:
            if self.any_tags.intersection(event.tags):
                pass
            else:
                return []
        if self.start_time:
            fb_end_time = self.parse_fb_timestamp(fb_event['info']['end_time'])
            if self.start_time < fb_end_time:
                pass
            else:
                return []
        if self.end_time:
            fb_start_time = parse_fb_timestamp(fb_event['info']['start_time'])
            if fb_start_time < self.end_time:
                pass
            else:
                return []
        if self.query_args:
            found_keyword = False
            for keyword in self.query_args:
                if keyword in fb_event['info']['name'] or keyword in fb_event['info']['description']:
                    found_keyword = True
            if found_keyword:
                pass
            else:
                return []
        if self.distance_in_km:
            distance = locations.get_distance(self.location[0], self.location[1], event.latitude, event.longitude, use_km=True)
            if distance < self.distance_in_km:
                pass
            else:
                return []
        return True
    
    def get_candidate_events(self):
        clauses = []
        bind_vars = {}
        if self.choreo_freestyle:
            clauses.append('search_tags = :search_tag')
            bind_vars['search_tag'] = self.choreo_freestyle
        if self.search_regions:
            clauses.append('search_regions in :search_regions')
            bind_vars['search_regions'] = self.search_regions
        if self.time_period:
            clauses.append('search_time_period = :search_time_period')
            bind_vars['search_time_period'] = self.time_period
        if clauses:
            full_clauses = ' and '.join('%s' % x for x in clauses)
            return eventdata.DBEvent.gql('where %s' % full_clauses, **bind_vars).fetch(100)
        else:
            return eventdata.DBEvent.all().fetch(100)

    def get_search_results(self, fb_uid, graph):
        # Do datastore filtering
        db_events = self.get_candidate_events()

        # Now look up contents of each event...
        batch_lookup = base_servlet.CommonBatchLookup(fb_uid, graph)
        for db_event in db_events:
            batch_lookup.lookup_event(db_event.fb_event_id)
        batch_lookup.finish_loading()

        # ...and do filtering based on the contents inside our app
        search_results = []
        for db_event in db_events:
            fb_event = batch_lookup.data_for_event(db_event.fb_event_id)
            if not fb_event['deleted'] and self.matches_event(db_event, fb_event):
                result = SearchResult(fb_uid, db_event, fb_event, self)
                search_results.append(result)
    
        # Now sort and return the results
        search_results.sort(key=lambda x: x.fb_event['info']['start_time'])
        return search_results

class SearchHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        self.display['freestyle_types'] = tags.FREESTYLE_EVENT_LIST
        self.display['choreo_types'] = tags.CHOREO_EVENT_LIST
        self.display['styles'] = tags.STYLES

        user_location = locations.get_geocoded_location(self.user.location)['latlng']
        nearest_city = cities.get_nearest_city(user_location[0], user_location[1])
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
        query = SearchQuery(self.parse_fb_timestamp, any_tags=tags_set, start_time=start_time, end_time=end_time)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)

        rsvps = rsvp.RSVPManager(self.batch_lookup)
        for result in search_results:
            result.rsvp_status = rsvps.get_rsvp_for_event(result.db_event.fb_event_id)
        self.display['results'] = search_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        self.render_template('results')

class RelevantHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
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
        query = SearchQuery(self.parse_fb_timestamp, time_period=tags.TIME_FUTURE, location=latlng_user_location, distance_in_km=distance_in_km)
        find_cities_within_km = distance_in_km + eventdata.REGION_RADIUS
        nearest_cities = cities.get_cities_within(latlng_user_location[0], latlng_user_location[1], distance_in_km=find_cities_within_km)
        query.search_regions = nearest_cities
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)

        rsvps = rsvp.RSVPManager(self.batch_lookup)
        for result in search_results:
            result.rsvp_status = rsvps.get_rsvp_for_event(result.db_event.fb_event_id)
        self.display['results'] = search_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        self.render_template('results')

