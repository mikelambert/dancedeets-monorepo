#!/usr/bin/env python

import datetime
import logging
import time
import smemcache

from google.appengine.ext import db

import base_servlet
from events import cities
from events import eventdata
from events import tags
from events import users
import fb_api
import locations
from logic import event_classifier
from logic import rsvp
from util import dates

class ResultsGroup(object): 
    def __init__(self, name, id, results, expanded, force=False): 
        self.name = name 
        self.id = id 
        self.results = results 
        self.expanded = expanded 
        self.force = force 

def group_results(search_results): 
    now = datetime.datetime.now() 

    grouped_results = [] 
    past_results = [] 
    present_results = [] 
    week_results = [] 
    month_results = [] 
    year_results = []
    for result in search_results: 
        if result.start_time < now: 
            if result.end_time > now:
                present_results.append(result)
            else: 
                past_results.append(result) 
        elif result.start_time < now + datetime.timedelta(days=7): 
            week_results.append(result)
        elif result.start_time < now + datetime.timedelta(days=30): 
            month_results.append(result)
        else: 
            year_results.append(result) 
    grouped_results.append(ResultsGroup('Events This Week', 'week_events', week_results, expanded=True)) 
    grouped_results.append(ResultsGroup('Events This Month', 'month_events', month_results, expanded=True)) 
    grouped_results.append(ResultsGroup('Future Events', 'year_events', year_results, expanded=True)) 
    grouped_results = [x for x in grouped_results if x.results]
    return past_results, present_results, grouped_results 

class SearchResult(object):
    def __init__(self, fb_user_id, db_event, fb_event, search_query):
        self.fb_user_id = fb_user_id
        self.db_event = db_event
        self.fb_event = fb_event
        self.search_query = search_query
        self.start_time = dates.parse_fb_timestamp(self.fb_event['info'].get('start_time'))
        self.end_time = dates.parse_fb_timestamp(self.fb_event['info'].get('end_time'))
        self.rsvp_status = "unknown"
        self.event_types = ', '.join(event_classifier.relevant_keywords(self.fb_event))
        self.attending_friend_count = 0
        self.attending_friends = []

    def multi_day_event(self):
        return (self.end_time - self.start_time) > datetime.timedelta(hours=24)

    def get_image(self):
        picture_url = self.fb_event.get('picture')
        if picture_url:
            return eventdata.get_event_image_url(picture_url, eventdata.EVENT_IMAGE_LARGE)
        else:
            logging.error("Error loading picture for event id %s", self.fb_event['info']['id'])
            logging.error("Data is %s\n\n%s", self.db_event, self.fb_event)
            return 'http://graph.facebook.com/%s/picture?type=large' % self.fb_event['info']['id']

    def get_attendance(self):
        if self.rsvp_status == 'unsure':
            return 'maybe'
        return self.rsvp_status

class SearchQuery(object):
    MATCH_TAGS = 'TAGS'
    MATCH_TIME = 'TIME'
    MATCH_LOCATION = 'LOCATION'
    MATCH_QUERY = 'QUERY'

    def __init__(self, any_tags=None, time_period=None, start_time=None, end_time=None, city_name=None, location=None, distance_in_km=None, query_args=None, dance_type=None, min_attendees=None):
        self.any_tags = set(any_tags or [])
        self.time_period = time_period
        self.dance_type = dance_type
                if dance_type == users.DANCE_TYPE_ALL_DANCE['internal']:
                        self.freestyle = users.FREESTYLE_DANCER
                        self.choreo = users.CHOREO_DANCER
                elif dance_type == users.DANCE_TYPE_FREESTYLE['internal']:
                        self.freestyle = users.FREESTYLE_DANCER
                        self.choreo = users.CHOREO_APATHY
                elif dance_type == users.DANCE_TYPE_CHOREO['internal']:
                        self.freestyle = users.FREESTYLE_APATHY
                        self.choreo = users.CHOREO_DANCER
                elif dance_type == users.DANCE_TYPE_FAN['internal']:
                        self.freestyle = users.FREESTYLE_FAN
                        self.choreo = users.CHOREO_FAN
                else:
                        assert False, 'unknown dance_type: %s' % dance_type

        self.min_attendees = min_attendees
        self.start_time = start_time
        self.end_time = end_time
        if self.start_time and self.end_time:
            assert self.start_time < self.end_time
        if self.time_period == tags.TIME_FUTURE and self.end_time:
                assert self.end_time > datetime.datetime.now()
        if self.time_period == tags.TIME_FUTURE and self.start_time:
                assert self.start_time < datetime.datetime.now()
        self.city_name = city_name
        self.location = location
        self.distance_in_km = distance_in_km
        self.query_args = query_args

        self.search_geohashes = []
        if self.location:
            self.search_geohashes = locations.get_all_geohashes_for(location[0], location[1], km=distance_in_km)
            logging.info("Searching geohashes %s", self.search_geohashes)

    def matches_db_event(self, event):
        if self.any_tags:
            if self.any_tags.intersection(event.tags):
                pass
            else:
                return []
        if self.start_time:
            if self.start_time < event.end_time:
                pass
            else:
                return []
        if self.end_time:
            if event.start_time < self.end_time:
                pass
            else:
                return []

        if self.min_attendees and event.attendee_count < self.min_attendees:
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
        if self.distance_in_km:
            distance = locations.get_distance(self.location[0], self.location[1], event.latitude, event.longitude, use_km=True)
            if distance < self.distance_in_km:
                pass
            else:
                return []
        return True

    def matches_fb_db_event(self, event, fb_event):
        if self.query_args:
            found_keyword = False
            for keyword in self.query_args:
                if keyword in fb_event['info']['name'] or keyword in fb_event['info'].get('description', ''):
                    found_keyword = True
            if found_keyword:
                pass
            else:
                return []
        return True
    
    def get_candidate_events(self):
        clauses = []
        bind_vars = {}
        if self.city_name:
            clauses.append('city_name = :city_name')
            bind_vars['city_name'] = self.city_name
        if self.search_geohashes:
            clauses.append('geohashes in :search_geohashes')
            bind_vars['search_geohashes'] = self.search_geohashes
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
        if self.start_time: # APPROXIMATION
            clauses.append('start_time > :start_time_min')
            bind_vars['start_time_min'] = self.start_time - datetime.timedelta(days=30)
        if self.end_time:
            clauses.append('start_time < :start_time_max')
            bind_vars['start_time_max'] = self.end_time
        if clauses:
            full_clauses = ' AND '.join('%s' % x for x in clauses)
            logging.info("Doing search with clauses: %s", full_clauses)
            return eventdata.DBEvent.gql('WHERE %s' % full_clauses, **bind_vars).fetch(1000)
        else:
            return eventdata.DBEvent.all().fetch(1000)

    def magical_get_candidate_events(self):
        a = time.time()
        search_events = get_search_index()
        event_ids = []
        for fb_event_id, (latitude, longitude) in search_events:
            distance = locations.get_distance(self.location[0], self.location[1], latitude, longitude, use_km=True)
            if distance < self.distance_in_km:
                event_ids.append(fb_event_id)
        logging.info("loading and filtering search index took %s seconds", time.time() - a)
        db_events = eventdata.get_cached_db_events(event_ids)
        return db_events

    def get_search_results(self, fb_uid, graph):
        db_events = None
        if self.time_period == tags.TIME_FUTURE and self.distance_in_km:
            # Use cached blob for our common case of filtering
            db_events = self.magical_get_candidate_events()
        if db_events is None:
            # Do datastore filtering
            db_events = self.get_candidate_events()

        # Do some obvious filtering before loading the fb events for each.
        db_events = [x for x in db_events if self.matches_db_event(x)]

        # Now look up contents of each event...
        a = time.time()
        batch_lookup = fb_api.CommonBatchLookup(fb_uid, graph)
        for db_event in db_events:
            batch_lookup.lookup_event(db_event.fb_event_id)
        batch_lookup.finish_loading()
        logging.info("loading fb data took %s seconds", time.time() - a)

        # ...and do filtering based on the contents inside our app
        search_results = []
        for db_event in db_events:
            fb_event = batch_lookup.data_for_event(db_event.fb_event_id)
            if not fb_event['deleted'] and self.matches_fb_db_event(db_event, fb_event):
                result = SearchResult(fb_uid, db_event, fb_event, self)
                search_results.append(result)
    
        # Now sort and return the results
        search_results.sort(key=lambda x: x.fb_event['info'].get('start_time'))
        return search_results

def construct_search_index():
    MAX_EVENTS = 5000
    db_events = db.Query(eventdata.DBEvent).filter('search_time_period =', tags.TIME_FUTURE).order('start_time').fetch(MAX_EVENTS)
    if len(db_events) >= MAX_EVENTS:
        slogging.error('Found %s future events. Increase the MAX_EVENTS limit to search more events.', MAX_EVENTS)

    search_events = [(x.fb_event_id, (x.latitude, x.longitude)) for x in db_events if x.latitude or x.longitude]
    return search_events

SEARCH_INDEX_MEMCACHE_KEY = 'SearchIndex'

def get_search_index(allow_cache=True):
    search_index = None
    if allow_cache:
        search_index = smemcache.get(SEARCH_INDEX_MEMCACHE_KEY)
    if not search_index:
        search_index = construct_search_index()
        smemcache.set(SEARCH_INDEX_MEMCACHE_KEY, search_index, time=2*3600)
    return search_index

EVENTS_AT_A_TIME = 200
def cache_fb_events(batch_lookup, search_index):
    """Load and stick fb events into cache."""
    if len(search_index) > EVENTS_AT_A_TIME:
        cache_fb_events(batch_lookup, search_index[EVENTS_AT_A_TIME:])
    search_index = search_index[:EVENTS_AT_A_TIME]
    batch_lookup = batch_lookup.copy()
    batch_lookup.allow_memcache = False
    for event_id, latlng in search_index:
        batch_lookup.lookup_event(event_id)
        batch_lookup.lookup_event_attending(event_id)
    logging.info("Loading %s events into memcache", len(search_index))
    batch_lookup.finish_loading()

def cache_db_events(search_index):
    """Load and stick db events into cache."""
    search_index = get_search_index()
    event_ids = [event_id for event_id, latlng in search_index]
    eventdata.get_cached_db_events(event_ids, allow_cache=False)

def recache_everything(batch_lookup):
    search_index = get_search_index(allow_cache=False)
    logging.info("Overall loading %s events into memcache", len(search_index))
    cache_fb_events(batch_lookup, search_index)
    cache_db_events(search_index)
