#!/usr/bin/env python

import datetime
import logging
import re
import time
import smemcache

from google.appengine.api import search
from google.appengine.ext import db
from google.appengine.ext import deferred

from events import eventdata
import fb_api
import locations
from util import dates
from util import timings

SLOW_QUEUE = 'slow-queue'

ALL_EVENTS_INDEX = 'AllEvents'
FUTURE_EVENTS_INDEX = 'FutureEvents'

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
    def __init__(self, pseudo_db_event, fb_event):
        self.fb_event = fb_event
        self.fb_event_id = fb_event['info']['id']
        self.actual_city_name = pseudo_db_event.actual_city_name
        self.attendee_count = pseudo_db_event.attendee_count
        self.start_time = dates.parse_fb_start_time(self.fb_event)
        self.end_time = dates.parse_fb_end_time(self.fb_event)
        self.fake_end_time = dates.parse_fb_end_time(self.fb_event, need_result=True)
        self.rsvp_status = "unknown"
        self.event_keywords = ', '.join(pseudo_db_event.event_keywords or [])
        self.attending_friend_count = 0
        self.attending_friends = []

        self.index = None

    def multi_day_event(self):
        return not self.end_time or (self.end_time - self.start_time) > datetime.timedelta(hours=24)

    def get_image(self):
        return eventdata.get_event_image_url(self.fb_event)

    def get_attendance(self):
        if self.rsvp_status == 'unsure':
            return 'maybe'
        return self.rsvp_status

class PseudoDBEvent(SearchResult):
    def __init__(self, d):
        self.fb_event_id = d.doc_id
        self.actual_city_name = d.field('actual_city_name').value
        self.attendee_count = 0
        # TODO(lambert): why doesn't this work?
        # self.attendee_count = d.field('attendee_count').value
        if self.attendee_count == 0:
            self.attendee_count = None
        self.event_keywords = d.field('event_keywords').value.split(', ')

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
        assert self.bounds

        self.search_geohashes = locations.get_all_geohashes_for(bounds)

        self.keywords = keywords

    def matches_db_event(self, event):
        if self.start_time:
            if self.start_time < self.fake_end_time:
                pass
            else:
                return False
        if self.end_time:
            if event.start_time < self.end_time:
                pass
            else:
                return False
        if self.time_period == eventdata.TIME_FUTURE:
            if self.fake_end_time < datetime.datetime.now():
                return False

        if self.min_attendees and event.attendee_count < self.min_attendees:
            return False

        if not locations.contains(self.bounds, (event.latitude, event.longitude)):
            return False

        return True

    def matches_fb_db_event(self, event, fb_event):
        return True
    
    DATE_SEARCH_FORMAT = '%Y-%m-%d'
    def get_new_candidate_events(self):
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
                clauses += ['(longitude <= %s OR longitude >= %s)' % longitudes]
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
            safe_keywords = re.sub(r'[<=>:()]', '', self.keywords)
            clauses += [safe_keywords]
        if clauses:
            full_search = ' '.join(clauses)
            logging.info("Doing search for %r", full_search)
            doc_index = search.Index(name=index_name)
            #TODO(lambert): implement pagination
            options = search.QueryOptions(
                limit=1000,
                returned_fields=['actual_city_name', 'attendee_count', 'event_keywords'])
            query = search.Query(query_string=full_search, options=options)
            doc_search_results = doc_index.search(query)
            search_results = []
            for x in doc_search_results:
                try:
                    search_results.append(PseudoDBEvent(x))
                except ValueError, e:
                    logging.error("Exception %s while constructing result for %s", e, x)
            return search_results

    def get_old_candidate_events(self):
        clauses = []
        bind_vars = {}
        if self.search_geohashes:
            clauses.append('geohashes in :search_geohashes')
            bind_vars['search_geohashes'] = self.search_geohashes
        if self.time_period:
            clauses.append('search_time_period = :search_time_period')
            bind_vars['search_time_period'] = self.time_period
        if self.start_time: # APPROXIMATION
            clauses.append('start_time > :start_time_min')
            bind_vars['start_time_min'] = self.start_time - datetime.timedelta(days=30)
        if self.end_time:
            clauses.append('start_time < :start_time_max')
            bind_vars['start_time_max'] = self.end_time
        if clauses:
            full_clauses = ' AND '.join('%s' % x for x in clauses)
            logging.info("Doing search with clauses: %s", full_clauses)
            full_clauses += " ORDER BY start_time DESC"
            return eventdata.DBEvent.gql('WHERE %s' % full_clauses, **bind_vars).fetch(500) #TODO(lambert): implement pagination if we want to go back further than this?
        else:
            return eventdata.DBEvent.all().fetch(500)

    def magical_get_candidate_events(self):
        a = time.time()
        search_events = get_search_index()
        event_ids = []
        for fb_event_id, (latitude, longitude) in search_events:
            if locations.contains(self.bounds, (latitude, longitude)):
                event_ids.append(fb_event_id)
        logging.info("loading and filtering search index took %s seconds", time.time() - a)
        db_events = eventdata.get_cached_db_events(event_ids)
        return db_events

    def get_search_results(self, fbl, new_search=True):
        db_events = None
        a = time.time()
        if self.time_period == eventdata.TIME_FUTURE and not new_search:
            # Use cached blob for our common case of filtering
            db_events = self.magical_get_candidate_events()
            logging.info("In-memory cache search returned %d events", len(db_events))
        if db_events is None:
            # Do datastore filtering
            if new_search:
                db_events = self.get_new_candidate_events()
                logging.info("New style search returned %s events", len(db_events))
            else:
                logging.info("Searching geohashes %s", self.search_geohashes)
                db_events = self.get_old_candidate_events()
                logging.info("Old style search returned %s events", len(db_events))
                orig_db_events_length = len(db_events)
                # Do some obvious filtering before loading the fb events for each.
                db_events = [x for x in db_events if self.matches_db_event(x)]
                logging.info("in-process filtering trimmed us from %s to % events", orig_db_events_length, len(db_events))
        logging.info("Using search index took %s seconds", time.time() - a)

        # Now look up contents of each event...
        a = time.time()
        fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in db_events])
        fbl.batch_fetch()
        logging.info("Loading fb data took %s seconds", time.time() - a)

        # ...and do filtering based on the contents inside our app
        a = time.time()
        search_results = []
        for db_event in db_events:
            fb_event = fbl.fetched_data(fb_api.LookupEvent, db_event.fb_event_id)
            if not fb_event['empty'] and self.matches_fb_db_event(db_event, fb_event):
                if 'info' not in fb_event:
                    logging.warning('%s', fb_event)
                result = SearchResult(db_event, fb_event)
                search_results.append(result)
        logging.info("dbevent in-memory filtering took %s seconds, leaving %s results", time.time() - a, len(search_results))
    
        # Now sort and return the results
        a = time.time()
        search_results.sort(key=lambda x: x.fb_event['info'].get('start_time'))
        logging.info("search result sorting took %s seconds", time.time() - a)
        return search_results

def update_fulltext_search_index(db_event, fb_event):
    doc_event = _create_doc_event(db_event, fb_event)
    if not doc_event: return
    logging.info("Adding event to search index: %s", db_event.fb_event_id)
    if db_event.search_time_period == eventdata.TIME_FUTURE:
        doc_index = search.Index(name=ALL_EVENTS_INDEX)
        doc_index.put(doc_event)
        doc_index = search.Index(name=FUTURE_EVENTS_INDEX)
        doc_index.put(doc_event)
    else:
        doc_index = search.Index(name=ALL_EVENTS_INDEX)
        doc_index.put(doc_event)
        doc_index = search.Index(name=FUTURE_EVENTS_INDEX)
        doc_index.delete(str(db_event.fb_event_id))

def delete_from_fulltext_search_index(db_event_id):
    logging.info("Deleting event from search index: %s", db_event_id)
    doc_index = search.Index(name=ALL_EVENTS_INDEX)
    doc_index.delete(str(db_event_id))
    doc_index = search.Index(name=FUTURE_EVENTS_INDEX)
    doc_index.delete(str(db_event_id))

def construct_fulltext_search_index(fbl, index_future=True):
    logging.info("Loading DB Events")
    MAX_EVENTS = 100000
    db_query = db.Query(eventdata.DBEvent, keys_only=True)
    if index_future:
        db_query = db_query.filter('search_time_period =', eventdata.TIME_FUTURE)
    db_event_keys = db_query.order('start_time').fetch(MAX_EVENTS)
    db_event_ids = set(x.id_or_name() for x in db_event_keys)

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
    doc_event = search.Document(
        doc_id=str(db_event.fb_event_id),
        fields=[
            search.TextField(name='keywords', value=fb_event['info'].get('name', '') + fb_event['info'].get('description', '')),
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
    db_events = eventdata.DBEvent.get_by_key_name(db_event_ids)
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
            delete_ids.append(str(db_event.fb_event_id))
            continue
        doc_events.append(doc_event)

    logging.info("Adding %s documents", len(doc_events))
    doc_index = search.Index(name=index_name)
    doc_index.put(doc_events)

    # These events could not be filtered out too early,
    # but only after looking up in this db+fb-event-data world
    logging.info("Cleaning up and deleting %s documents", len(delete_ids))
    doc_index.delete(delete_ids)

def construct_search_index():
    MAX_EVENTS = 10000
    db_events = db.Query(eventdata.DBEvent).filter('search_time_period =', eventdata.TIME_FUTURE).order('start_time').fetch(MAX_EVENTS)
    eventdata.cache_db_events(db_events)
    if len(db_events) >= MAX_EVENTS:
        logging.critical('Found %s future events. Increase the MAX_EVENTS limit to search more events.', MAX_EVENTS)

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

# since _inner_cache_fb_events is a decorated function, it can't be pickled, which breaks deferred. so make this wrapper function here.
def cache_fb_events(fbl, search_index):
    _inner_cache_fb_events(fbl, search_index)

EVENTS_AT_A_TIME = 200
@timings.timed
def _inner_cache_fb_events(fbl, search_index):
    """Load and stick fb events into cache."""
    if len(search_index) > EVENTS_AT_A_TIME:
        deferred.defer(cache_fb_events, fbl, search_index[EVENTS_AT_A_TIME:], _queue=SLOW_QUEUE)
        search_index = search_index[:EVENTS_AT_A_TIME]
    fbl.allow_memcache_read = False
    event_ids = [event_id for event_id, latlng in search_index]
    fbl.request_multi(fb_api.LookupEvent, event_ids)
    fbl.request_multi(fb_api.LookupEventAttending, event_ids)
    logging.info("Loading %s events into memcache", len(search_index))
    fbl.batch_fetch()

@timings.timed
def recache_everything(fbl):
    search_index = get_search_index(allow_cache=False)
    logging.info("Overall loading %s events into memcache", len(search_index))
    deferred.defer(cache_fb_events, fbl, search_index, _queue=SLOW_QUEUE)
    # caching of db events is done automatically by construct_search_index since it already has the db events loaded
