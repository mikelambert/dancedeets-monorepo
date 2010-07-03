#!/usr/bin/env python

import datetime

import base_servlet
from events import cities
from events import eventdata
from events import tags
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

    def __init__(self, parse_fb_timestamp, any_tags=None, start_time=None, end_time=None, location=None, distance=None, query_args=None):
        self.parse_fb_timestamp = parse_fb_timestamp
        self.any_tags = set(any_tags)
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.distance = distance
        self.query_args = query_args
        self.matches = set()

    def matches_event(self, event, fb_event):
        if self.any_tags:
            if self.any_tags.intersection(event.tags):
                self.matches.add(SearchQuery.MATCH_TAGS)
            else:
                return []
        if self.start_time:
            fb_end_time = self.parse_fb_timestamp(fb_event['info']['end_time'])
            if self.start_time < fb_end_time:
                self.matches.add(SearchQuery.MATCH_TIME)
            else:
                return []
        if self.end_time:
            fb_start_time = parse_fb_timestamp(fb_event['info']['start_time'])
            if fb_start_time < self.end_time:
                self.matches.add(SearchQuery.MATCH_TIME)
            else:
                return []
        if self.query_args:
            found_keyword = False
            for keyword in self.query_args:
                if keyword in fb_event['info']['name'] or keyword in fb_event['info']['description']:
                    found_keyword = True
            if found_keyword:
                self.matches.add(SearchQuery.MATCH_QUERY)
            else:
                return []

        return self.matches
    
    def get_candidate_events(self):
        clauses = []
        bind_vars = {}
        if self.any_tags:
            clauses.append('tags in :tags')
            bind_vars['tags'] = list(self.any_tags)
            #TODO(lambert): make list queries more efficient by supporting "any choreo", "any freestyle", "any style", etc? wait until we hash out our UI more...
            self.matches.add(SearchQuery.MATCH_TAGS)

        if self.start_time:
            clauses.append('start_time > :start_time')
            bind_vars['start_time'] = self.start_time
            self.matches.add(SearchQuery.MATCH_TIME)
        elif self.end_time:
            clauses.append('end_time > :end_time')
            bind_vars['end_time'] = self.end_time
            self.matches.add(SearchQuery.MATCH_TIME)
        #TODO(lambert): implement searching in the appengine backend for multi-time-location queries
        # ...use prebucketed time/locations (by latlong grid, buckets of time)
        #TODO(lambert): implement simple keyword searches here?
        full_clauses = ' and '.join('%s' % x for x in clauses)
        return eventdata.DBEvent.gql('where %s' % full_clauses, **bind_vars).fetch(100)

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
        import logging
        logging.info("a %s %s",self.user.location, user_location)
        sorted_cities = cities.sort_by_closest(user_location[0], user_location[1])
        sorted_cities = [': '.join(reversed(x.split(', '))) for x in sorted_cities]
        self.display['cities'] = sorted_cities
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

