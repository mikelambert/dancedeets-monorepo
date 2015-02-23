#!/usr/bin/env python

import datetime
import logging
import re
import time

from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.ext import deferred

from events import eventdata
import fb_api
from loc import gmaps_api
from loc import math
from util import dates
from util import timings

SLOW_QUEUE = 'slow-queue'

ALL_EVENTS_INDEX = 'AllEvents'
FUTURE_EVENTS_INDEX = 'FutureEvents'

MAX_EVENTS = 100000

class ResultsGroup(object): 
    def __init__(self, name, id, results, expanded, force=False): 
        self.name = name 
        self.id = id 
        self.results = results 
        self.expanded = expanded 
        self.force = force 

def group_results(search_results): 
    now = datetime.datetime.now() - datetime.timedelta(hours=12)

    grouped_results = [] 
    past_results = [] 
    present_results = [] 
    week_results = [] 
    month_results = [] 
    year_results = []
    past_index = 0
    future_index = 0
    for result in search_results: 
        if result.start_time < now:
            result.index = past_index
            past_index += 1
            if result.fake_end_time > now:
                present_results.append(result)
            else: 
                past_results.append(result) 
        else:
            result.index = future_index
            future_index += 1
            if result.start_time < now + datetime.timedelta(days=7): 
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
    def __init__(self, db_event, fb_event):
        self.db_event = db_event
        self.fb_event = fb_event
        self.fb_event_id = fb_event['info']['id']
        self.actual_city_name = db_event.actual_city_name
        self.attendee_count = db_event.attendee_count
        self.start_time = dates.parse_fb_start_time(self.fb_event)
        self.end_time = dates.parse_fb_end_time(self.fb_event)
        self.fake_end_time = dates.parse_fb_end_time(self.fb_event, need_result=True)
        self.rsvp_status = "unknown"
        self.event_keywords = db_event.event_keywords or []
        # These are initialized in logic/friends.py
        self.attending_friend_count = 0
        self.attending_friends = []

        self.index = None

    def event_keywords_string(self):
        return ', '.join(self.event_keywords)

    def multi_day_event(self):
        return not self.end_time or (self.end_time - self.start_time) > datetime.timedelta(hours=24)

    def get_image(self):
        return eventdata.get_event_image_url(self.fb_event)

    def get_attendance(self):
        if self.rsvp_status == 'unsure':
            return 'maybe'
        return self.rsvp_status

class PseudoDBEvent(object):
    def __init__(self, d):
        self.fb_event_id = d.doc_id
        self.actual_city_name = d.field('actual_city_name').value
        self.attendee_count = 0
        # TODO(lambert): why doesn't this work?
        # self.attendee_count = d.field('attendee_count').value
        if self.attendee_count == 0:
            self.attendee_count = None
        self.event_keywords = d.field('event_keywords').value.split(', ')
        self._search_result = d

class SearchQuery(object):
    def __init__(self, time_period=None, start_time=None, end_time=None, bounds=None, min_attendees=None, keywords=None):
        self.time_period = time_period

        self.min_attendees = min_attendees
        self.start_time = start_time
        self.end_time = end_time
        if self.start_time and self.end_time:
            assert self.start_time < self.end_time
        if self.time_period == eventdata.TIME_FUTURE and self.end_time:
                assert self.end_time > datetime.datetime.now()
        if self.time_period == eventdata.TIME_FUTURE and self.start_time:
                assert self.start_time < datetime.datetime.now()
        self.bounds = bounds

        self.keywords = keywords

        self.limit = 1000

        # Extra search index fields to return
        self.extra_fields = []

    @classmethod
    def create_from_query(cls, query, start_end_query=False):
        if query.location:
            if query.distance_units == 'miles':
                distance_in_km = math.miles_in_km(query.distance)
            else:
                distance_in_km = query.distance
            geocode = gmaps_api.get_geocode(address=query.location)
            bounds = math.expand_bounds(geocode.latlng_bounds(), distance_in_km)
        else:
            bounds = None
        if start_end_query:
            self = cls(bounds=bounds, min_attendees=query.min_attendees, keywords=query.keywords, start_time=query.start_time, end_time=query.end_time)
        else:
            if query.past:
                time_period = eventdata.TIME_PAST
            else:
                time_period = eventdata.TIME_FUTURE
            self = cls(bounds=bounds, min_attendees=query.min_attendees, keywords=query.keywords, time_period=time_period)
        return self

    DATE_SEARCH_FORMAT = '%Y-%m-%d'
    def get_candidate_dbevents(self):
        clauses = []
        if self.bounds:
            # We try to keep searches as simple as possible, 
            # using just AND queries on latitude/longitude.
            # But for stuff crossing +/-180 degrees,
            # we need to do an OR longitude query on each side.
            latitudes = (self.bounds[0][0], self.bounds[1][0])
            longitudes = (self.bounds[0][1], self.bounds[1][1])
            clauses += ['latitude >= %s AND latitude <= %s' % latitudes]
            if longitudes[0] < longitudes[1]:
                clauses += ['longitude >= %s AND longitude <= %s' % longitudes]
            else:
                clauses += ['(longitude >= %s OR longitude <= %s)' % longitudes]
        index_name = ALL_EVENTS_INDEX
        if self.time_period:
            if self.time_period == eventdata.TIME_FUTURE:
                index_name = FUTURE_EVENTS_INDEX
        if self.start_time:
            # Do we want/need this hack?
            if self.start_time > datetime.datetime.now():
                index_name = FUTURE_EVENTS_INDEX
            clauses += ['end_time >= %s' % self.start_time.date().strftime(self.DATE_SEARCH_FORMAT)]
        if self.end_time:
            clauses += ['start_time <= %s' % self.end_time.date().strftime(self.DATE_SEARCH_FORMAT)]
        if self.keywords:
            safe_keywords = re.sub(r'[<=>:(),]', ' ', self.keywords)
            clauses += ['(%s)' % safe_keywords]
        if clauses:
            full_search = ' '.join(clauses)
            logging.info("Doing search for %r", full_search)
            doc_index = search.Index(name=index_name)
            #TODO(lambert): implement pagination
            options = search.QueryOptions(
                limit=self.limit,
                returned_fields=['actual_city_name', 'attendee_count', 'event_keywords'] + self.extra_fields)
            query = search.Query(query_string=full_search, options=options)
            doc_search_results = doc_index.search(query)
            db_events = []
            for x in doc_search_results:
                try:
                    db_events.append(PseudoDBEvent(x))
                except ValueError, e:
                    logging.error("Exception %s while constructing result for %s", e, x)
            return db_events

    def get_search_results(self, fbl, prefilter=None):
        a = time.time()
        # Do datastore filtering
        db_events = self.get_candidate_dbevents()
        logging.info("Search returned %s events in %s seconds", len(db_events), time.time() - a)

        if prefilter:
            db_events = [x for x in db_events if prefilter(x)]

        a = time.time()
        real_db_events = eventdata.DBEvent.get_by_ids([x.fb_event_id for x in db_events])
        logging.info("Loading DBEvents took %s seconds", time.time() - a)

        # ...and do filtering based on the contents inside our app
        a = time.time()
        search_results = []
        for real_db_event, db_event in zip(real_db_events, db_events):
            fb_event = real_db_event.fb_event
            if not fb_event:
                logging.error("Failed to find fb_event on db_event %s", real_db_event.fb_event_id)
                continue
            if not fb_event['empty']:
                if 'info' not in fb_event:
                    logging.warning('%s', fb_event)
                result = SearchResult(real_db_event, fb_event)
                search_results.append(result)
        logging.info("SearchResult construction took %s seconds, giving %s results", time.time() - a, len(search_results))
    
        # Now sort and return the results
        a = time.time()
        search_results.sort(key=lambda x: x.fb_event['info'].get('start_time'))
        logging.info("search result sorting took %s seconds", time.time() - a)
        return search_results

def update_fulltext_search_index(db_event, fb_event):
    logging.info("Adding event to search index: %s", db_event.fb_event_id)
    doc_event = _create_doc_event(db_event, fb_event)
    if not doc_event: return
    if db_event.search_time_period == eventdata.TIME_FUTURE:
        doc_index = search.Index(name=ALL_EVENTS_INDEX)
        doc_index.put(doc_event)
        doc_index = search.Index(name=FUTURE_EVENTS_INDEX)
        doc_index.put(doc_event)
    else:
        doc_index = search.Index(name=ALL_EVENTS_INDEX)
        doc_index.put(doc_event)
        doc_index = search.Index(name=FUTURE_EVENTS_INDEX)
        doc_index.delete(db_event.fb_event_id)

def delete_from_fulltext_search_index(db_event_id):
    logging.info("Deleting event from search index: %s", db_event_id)
    doc_index = search.Index(name=ALL_EVENTS_INDEX)
    doc_index.delete(db_event_id)
    doc_index = search.Index(name=FUTURE_EVENTS_INDEX)
    doc_index.delete(db_event_id)

def construct_fulltext_search_index(fbl, index_future=True):
    logging.info("Loading DB Events")
    if index_future:
        db_query = eventdata.DBEvent.query(eventdata.DBEvent.search_time_period==eventdata.TIME_FUTURE)
    else:
        db_query = eventdata.DBEvent.query()
    db_event_keys = db_query.fetch(MAX_EVENTS, keys_only=True)
    db_event_ids = set(x.string_id() for x in db_event_keys)

    logging.info("Found %s db event ids for indexing", len(db_event_ids))
    if len(db_event_ids) >= MAX_EVENTS:
        logging.critical('Found %s events. Increase the MAX_EVENTS limit to search more events.', MAX_EVENTS)
    logging.info("Loaded %s DB Events", len(db_event_ids))

    index_name = index_future and FUTURE_EVENTS_INDEX or ALL_EVENTS_INDEX
    doc_index = search.Index(name=index_name)

    docs_per_group = search.MAXIMUM_DOCUMENTS_PER_PUT_REQUEST

    logging.info("Deleting Expired DB Events")
    start_id = '0'
    doc_ids_to_delete = set()
    while True:
        doc_ids = [x.doc_id for x in doc_index.get_range(ids_only=True, start_id=start_id, include_start_object=False)]
        if not doc_ids:
            break
        new_ids_to_delete = set(doc_ids).difference(db_event_ids)
        doc_ids_to_delete.update(new_ids_to_delete)
        logging.info("Looking at %s doc_id candidates for deletion, will delete %s entries.", len(doc_ids), len(new_ids_to_delete))
        start_id = doc_ids[-1]
    if len(doc_ids_to_delete) and len(doc_ids_to_delete) < len(db_event_ids) / 10:
        logging.critical("Deleting %s docs, more than 10% of total %s docs", len(doc_ids_to_delete), len(db_event_ids))
    logging.info("Deleting %s Events", len(doc_ids_to_delete))
    doc_ids_to_delete = list(doc_ids_to_delete)
    for i in range(0,len(doc_ids_to_delete), docs_per_group):
        doc_index.delete(doc_ids_to_delete[i:i+docs_per_group])

    # Add all events
    logging.info("Loading %s FB Events, in groups of %s", len(db_event_ids), docs_per_group)
    db_event_ids_list = list(db_event_ids)
    for i in range(0,len(db_event_ids_list), docs_per_group):
        group_db_event_ids = db_event_ids_list[i:i+docs_per_group]
        deferred.defer(save_db_event_ids, fbl, index_name, group_db_event_ids)

def _create_doc_event(db_event, fb_event):
    if fb_event['empty']:
        return None
    # TODO(lambert): find a way to index no-location events.
    # As of now, the lat/long number fields cannot be None.
    # In what radius/location should no-location events show up
    # and how do we want to return them
    # Perhaps a separate index that is combined at search-time?
    if db_event.latitude is None:
        return None
    # If this event has been deleted from Facebook, let's skip re-indexing it here
    if db_event.start_time is None:
        return None
    if not isinstance(db_event.start_time, datetime.datetime) and not isinstance(db_event.start_time, datetime.date):
        logging.error("DB Event %s start_time is not correct format: ", db_event.fb_event_id, db_event.start_time)
        return None
    doc_event = search.Document(
        doc_id=db_event.fb_event_id,
        fields=[
            search.TextField(name='keywords', value=fb_event['info'].get('name', '') + '\n\n' + fb_event['info'].get('description', '')),
            search.NumberField(name='attendee_count', value=db_event.attendee_count or 0),
            search.DateField(name='start_time', value=db_event.start_time),
            search.DateField(name='end_time', value=dates.faked_end_time(db_event.start_time, db_event.end_time)),
            search.NumberField(name='latitude', value=db_event.latitude),
            search.NumberField(name='longitude', value=db_event.longitude),
            search.TextField(name='actual_city_name', value=db_event.actual_city_name),
            search.TextField(name='event_keywords', value=', '.join(db_event.event_keywords)),
        ],
        #language=XX, # We have no good language detection
        rank=int(time.mktime(db_event.start_time.timetuple())),
        )
    return doc_event

def save_db_event_ids(fbl, index_name, db_event_ids):
    # TODO(lambert): how will we ensure we only update changed events?
    logging.info("Loading %s DB Events", len(db_event_ids))
    db_events = eventdata.DBEvent.get_by_ids(db_event_ids)
    if None in db_events:
        logging.error("DB Event Lookup returned None!")
    logging.info("Loading %s FB Events", len(db_event_ids))
    fbl.request_multi(fb_api.LookupEvent, db_event_ids)
    fbl.batch_fetch()

    delete_ids = []
    doc_events = []
    logging.info("Constructing Documents")
    for db_event in db_events:
        fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id)
        doc_event = _create_doc_event(db_event, fb_event)
        if not doc_event:
            delete_ids.append(db_event.fb_event_id)
            continue
        doc_events.append(doc_event)

    logging.info("Adding %s documents", len(doc_events))
    doc_index = search.Index(name=index_name)
    doc_index.put(doc_events)

    # These events could not be filtered out too early,
    # but only after looking up in this db+fb-event-data world
    logging.info("Cleaning up and deleting %s documents", len(delete_ids))
    doc_index.delete(delete_ids)

# since _inner_cache_fb_events is a decorated function, it can't be pickled, which breaks deferred. so make this wrapper function here.
def cache_fb_events(fbl, event_ids):
    _inner_cache_fb_events(fbl, event_ids)

@timings.timed
def _inner_cache_fb_events(fbl, event_ids):
    """Load and stick fb events into cache."""
    # Force write to memcache for memcache-fetched objects (and db-fetched objects)
    fbl.resave_to_memcache = True
    fbl.request_multi(fb_api.LookupEvent, event_ids)
    fbl.request_multi(fb_api.LookupEventAttending, event_ids)
    logging.info("Loading %s events into memcache", len(event_ids))
    fbl.batch_fetch()

@timings.timed
def memcache_future_events(fbl):
    db_query = eventdata.DBEvent.query(eventdata.DBEvent.search_time_period==eventdata.TIME_FUTURE)
    event_ids = [x.id() for x in db_query.fetch(MAX_EVENTS, keys_only=True)]
    logging.info("Overall loading %s events into memcache", len(event_ids))
    EVENTS_AT_A_TIME = 200
    for i in range(0, len(event_ids), EVENTS_AT_A_TIME):
        deferred.defer(cache_fb_events, fbl, event_ids[i:i+EVENTS_AT_A_TIME], _queue=SLOW_QUEUE)
