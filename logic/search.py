#!/usr/bin/env python

import datetime
import logging

import base_servlet
from events import cities
from events import eventdata
from events import tags
from events import users
import fb_api
from logic import rsvp
import locations


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
        self.start_time = eventdata.parse_fb_timestamp(self.fb_event['info']['start_time'])
        self.end_time = eventdata.parse_fb_timestamp(self.fb_event['info']['end_time'])
        results = eventdata.get_geocoded_location_for_event(db_event, fb_event)
        self.city = results['city']
        self.rsvp_status = "unknown"
        if self.db_event:
            tag_lookup = [tags.EVENT_TYPE_LOOKUP[x] for x in db_event.tags]
            self.event_types = ', '.join(sorted(tag_lookup))
        else:
            self.event_types = None
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

    def matches_event(self, event, fb_event):
        if self.any_tags:
            if self.any_tags.intersection(event.tags):
                pass
            else:
                return []
        if self.start_time:
            fb_end_time = eventdata.parse_fb_timestamp(fb_event['info']['end_time'])
            if self.start_time < fb_end_time:
                pass
            else:
                return []
        if self.end_time:
            fb_start_time = eventdata.parse_fb_timestamp(fb_event['info']['start_time'])
            if fb_start_time < self.end_time:
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

        if self.query_args:
            found_keyword = False
            for keyword in self.query_args:
                if keyword in fb_event['info']['name'] or keyword in fb_event['info'].get('description', ''):
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
            full_clauses = ' and '.join('%s' % x for x in clauses)
            logging.info("Doing search with clauses: %s", full_clauses)
            return eventdata.DBEvent.gql('where %s' % full_clauses, **bind_vars).fetch(1000)
        else:
            return eventdata.DBEvent.all().fetch(100)

    def get_search_results(self, fb_uid, graph):
        # Do datastore filtering
        db_events = self.get_candidate_events()

        # Now look up contents of each event...
        batch_lookup = fb_api.CommonBatchLookup(fb_uid, graph)
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

