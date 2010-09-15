#!/usr/bin/env python

import datetime
import logging

import base_servlet
from events import cities
from events import eventdata
from events import tags
from events import users
from logic import rsvp
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
        picture_url = self.fb_event.get('picture')
        if picture_url:
            return eventdata.get_event_image_url(picture_url, eventdata.EVENT_IMAGE_MEDIUM)
        else:
            logging.error("Error loading picture for event id %s", self.db_event.fb_event_id)
            logging.error("Data is %s\n\n%s", self.db_event, self.fb_event)
            return 'http://graph.facebook.com/331218348435/picture' % self.db_event.fb_event_id

    def get_attendance(self):
        if self.rsvp_status == 'unsure':
            return 'maybe'
        return self.rsvp_status

class SearchQuery(object):
    MATCH_TAGS = 'TAGS'
    MATCH_TIME = 'TIME'
    MATCH_LOCATION = 'LOCATION'
    MATCH_QUERY = 'QUERY'

    def __init__(self, parse_fb_timestamp, any_tags=None, choreo_freestyle=None, time_period=None, start_time=None, end_time=None, location=None, distance_in_km=None, query_args=None, freestyle=None, choreo=None):
        self.parse_fb_timestamp = parse_fb_timestamp
        self.any_tags = set(any_tags or [])
        self.choreo_freestyle = choreo_freestyle
        self.time_period = time_period
        self.freestyle = freestyle
        self.choreo = choreo
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

        find_cities_within_km = distance_in_km + eventdata.REGION_RADIUS
        nearest_cities = cities.get_cities_within(location[0], location[1], distance_in_km=find_cities_within_km)
        self.search_regions = nearest_cities

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

        search_tags = []
        if self.choreo == users.CHOREO_FAN:
            search_tags.extend(tags.CHOREO_FAN_EVENTS)
        elif self.choreo == users.CHOREO_DANCER:
            search_tags.extend(x[0] for x in tags.CHOREO_EVENT_LIST)
        if self.freestyle == users.FREESTYLE_FAN:
            search_tags.extend(tags.FREESTYLE_FAN_EVENTS)
        elif self.freestyle == users.FREESTYLE_DANCER:
            search_tags.extend(x[0] for x in tags.FREESTYLE_EVENT_LIST)
        intersecting_tags = set(search_tags).intersection(event.tags)
        if intersecting_tags:
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
        search_tags = []
        if self.choreo != users.CHOREO_APATHY:
            search_tags.append(tags.CHOREO_EVENT)
        if self.freestyle != users.FREESTYLE_APATHY:
            search_tags.append(tags.FREESTYLE_EVENT)
        if len(search_tags) == 0:
            clauses.append('search_tags = "nonexistent"')
        elif len(search_tags) == 1:
            clauses.append('search_tags = :search_tags')
            bind_vars['search_tags'] = search_tags[0]
        elif len(search_tags) == 2:
            pass # retrieve everything!
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

