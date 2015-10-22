#!/usr/bin/env python

import collections
import datetime
import logging
import pprint
import re
import time

from google.appengine.ext import ndb
from google.appengine.api import search

from events import eventdata
from loc import gmaps_api
from loc import math
from nlp import categories
from util import dates
from . import index
from . import search_base

SLOW_QUEUE = 'slow-queue'

MAX_EVENTS = 100000

class ResultsGroup(object):
    def __init__(self, name, results):
        self.name = name
        self.results = results

def group_results(search_results, include_all=False):
    now = datetime.datetime.now() - datetime.timedelta(hours=12)

    grouped_results = []
    past_results = []
    present_results = []
    week_results = []
    month_results = []
    year_results = []
    for result in search_results:
        if result.start_time < now:
            if result.fake_end_time > now:
                present_results.append(result)
            else:
                past_results.append(result)
        else:
            if result.start_time < now + datetime.timedelta(days=7):
                week_results.append(result)
            elif result.start_time < now + datetime.timedelta(days=30):
                month_results.append(result)
            else:
                year_results.append(result)
    grouped_results.append(ResultsGroup('Events This Week', week_results))
    grouped_results.append(ResultsGroup('Events This Month', month_results))
    grouped_results.append(ResultsGroup('Future Events', year_results))
    if not include_all:
        grouped_results = [x for x in grouped_results if x.results]
    return past_results, present_results, grouped_results

class DisplayEvent(ndb.Model):
    """Subset of event data used for rendering"""
    fb_event_id = property(lambda x: str(x.key.string_id()))

    data = ndb.JsonProperty()

    @classmethod
    def can_build_from(cls, db_event):
        """Can we build a DisplayEvent from a given DBEvent"""
        if not db_event.fb_event:
            return False
        elif db_event.fb_event['empty']:
            return False
        else:
            return True

    @classmethod
    def build(cls, db_event):
        """Save off the minimal set of data necessary to render an event, for quick event loading."""
        if not cls.can_build_from(db_event):
            return None
        try:
            display_event = cls(id=db_event.fb_event_id)
            # The event_keywords are actually _BaseValue objects, not strings.
            # So they fail json serialization, and must be converted manually here.
            keywords = [unicode(x) for x in db_event.event_keywords]
            categories = [unicode(x) for x in db_event.auto_categories]
            display_event.data = {
                'name': db_event.fb_event['info'].get('name'),
                'image': eventdata.get_event_image_url(db_event.fb_event),
                'cover': eventdata.get_largest_cover(db_event.fb_event),
                'start_time': db_event.fb_event['info']['start_time'],
                'end_time': db_event.fb_event['info'].get('end_time'),
                'location': db_event.actual_city_name,
                'lat': db_event.latitude,
                'lng': db_event.longitude,
                'attendee_count': db_event.attendee_count,
                'categories': categories,
                'keywords': keywords,
            }
            return display_event
        except:
            logging.exception("Failed to construct DisplayEvent for event %s", db_event.fb_event_id)
            logging.error("FB Event data is:\n%s", pprint.pformat(db_event.fb_event, width=200))
            return None

    @classmethod
    def get_by_ids(cls, id_list, keys_only=False):
        if not id_list:
            return []
        keys = [ndb.Key(cls, x) for x in id_list]
        if keys_only:
            return cls.query(cls.key.IN(keys)).fetch(len(keys), keys_only=True)
        else:
            return ndb.get_multi(keys)

class SearchQuery(object):
    def __init__(self, time_period=None, start_date=None, end_date=None, bounds=None, min_attendees=None, keywords=None):
        self.time_period = time_period

        self.min_attendees = min_attendees
        self.start_date = start_date
        self.end_date = end_date
        if self.start_date and self.end_date:
            assert self.start_date < self.end_date
        if self.time_period in search_base.FUTURE_INDEX_TIMES and self.end_date:
            assert self.end_date > datetime.date.today()
        if self.time_period in search_base.FUTURE_INDEX_TIMES and self.start_date:
            assert self.start_date < datetime.date.today()
        self.bounds = bounds

        if keywords:
            unquoted_quoted_keywords = re.sub(r'[<=>:(),]', ' ', keywords).split('"')
            for i in range(0, len(unquoted_quoted_keywords), 2):
                unquoted_quoted_keywords[i] = categories.format_as_search_query(unquoted_quoted_keywords[i])
            reconstructed_keywords = '"'.join(unquoted_quoted_keywords)
            self.keywords = reconstructed_keywords
        else:
            self.keywords = None

        self.limit = 1000

        # Extra search index fields to return
        self.extra_fields = []

    @classmethod
    def create_from_form(cls, form, start_end_query=False):
        if form.location.data:
            geocode = gmaps_api.get_geocode(address=form.location.data)
            if not geocode:
                raise search_base.SearchException("Did not understand location: %s" % form.location.data)
            bounds = math.expand_bounds(geocode.latlng_bounds(), form.distance_in_km())
        else:
            bounds = None
        common_fields = dict(bounds=bounds, min_attendees=form.min_attendees.data, keywords=form.keywords.data)
        if start_end_query:
            self = cls(start_date=form.start.data, end_date=form.end.data, **common_fields)
        else:
            self = cls(time_period=form.time_period.data, **common_fields)
        return self

    DATE_SEARCH_FORMAT = '%Y-%m-%d'
    def _get_query_string(self):
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
        if self.start_date:
            clauses += ['end_time >= %s' % self.start_date.strftime(self.DATE_SEARCH_FORMAT)]
        if self.end_date:
            clauses += ['start_time <= %s' % self.end_date.strftime(self.DATE_SEARCH_FORMAT)]
        if self.keywords and self.keywords.strip():
            clauses += ['(%s)' % self.keywords.strip()]
        if self.min_attendees:
            clauses += ['attendee_count > %d' % self.min_attendees]
        if clauses:
            return ' '.join(clauses)
        else:
            return None

    def _get_candidate_doc_events(self, ids_only=True):
        query_string = self._get_query_string()
        if not query_string:
            return []

        search_index = AllEventsIndex
        if self.time_period:
            if self.time_period in search_base.FUTURE_INDEX_TIMES:
                search_index = FutureEventsIndex
        if self.start_date:
            # Do we want/need this hack?
            if self.start_date > datetime.date.today():
                search_index = FutureEventsIndex

        logging.info("Doing search for %r", query_string)
        doc_index = search_index.real_index()
        #TODO(lambert): implement pagination
        if ids_only:
            options = {'returned_fields': ['start_time', 'end_time']}
        else:
            options = {'returned_fields': self.extra_fields}
        options = search.QueryOptions(limit=self.limit, **options)
        query = search.Query(query_string=query_string, options=options)
        doc_search_results = doc_index.search(query)
        return doc_search_results.results

    @staticmethod
    def _deduped_results(search_results):
        existing_datetime_locs = collections.defaultdict(lambda: [])
        for r in search_results:
            existing_datetime_locs[(r.start_time, r.latitude, r.longitude)].append(r)

        deduped_results = []
        for same_results in existing_datetime_locs.values():
            largest_result = max(same_results, key=lambda x: x.attendee_count)
            deduped_results.append(largest_result)
        return deduped_results

    def get_search_results(self, prefilter=None, full_event=False):
        a = time.time()
        # Do datastore filtering
        doc_events = self._get_candidate_doc_events(ids_only=not prefilter)
        logging.info("Search returned %s events in %s seconds", len(doc_events), time.time() - a)

        #TODO(lambert): move to common library.
        now = datetime.datetime.now() - datetime.timedelta(hours=12)
        if self.time_period == search_base.TIME_ONGOING:
            doc_events = [x for x in doc_events if x.field('start_time').value < now]
        elif self.time_period == search_base.TIME_UPCOMING:
            doc_events = [x for x in doc_events if x.field('start_time').value > now]
        elif self.time_period == search_base.TIME_PAST:
            doc_events = [x for x in doc_events if x.field('end_time').value < now]
        elif self.time_period == search_base.TIME_ALL_FUTURE:
            pass
        else:
            # Calendar searches that use start/end time ranges uses this
            pass

        if prefilter:
            doc_events = [x for x in doc_events if prefilter(x)]

        logging.info("After filtering, we have %s events", len(doc_events))

        a = time.time()
        ids = [x.doc_id for x in doc_events]
        if full_event:
            real_db_events = eventdata.DBEvent.get_by_ids(ids)
            display_events = [DisplayEvent.build(x) for x in real_db_events]
        else:
            display_events = DisplayEvent.get_by_ids(ids)
            real_db_events = [None for x in ids]

        logging.info("Loading DBEvents took %s seconds", time.time() - a)

        # ...and do filtering based on the contents inside our app
        a = time.time()
        search_results = []
        for display_event, db_event in zip(display_events, real_db_events):
            if not display_event:
                continue
            result = search_base.SearchResult(display_event.fb_event_id, display_event.data, db_event)
            search_results.append(result)
        logging.info("SearchResult construction took %s seconds, giving %s results", time.time() - a, len(search_results))
    
        search_results = self._deduped_results(search_results)

        # Now sort and return the results
        search_results.sort(key=lambda x: x.start_time)
        return search_results

class EventsIndex(index.BaseIndex):
    obj_type = eventdata.DBEvent

    @classmethod
    def _create_doc_event(cls, db_event):
        fb_event = db_event.fb_event
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
                search.TextField(name='name', value=fb_event['info'].get('name', '')),
                search.TextField(name='description', value=fb_event['info'].get('description', '')),
                search.NumberField(name='attendee_count', value=db_event.attendee_count or 0),
                search.DateField(name='start_time', value=db_event.start_time),
                search.DateField(name='end_time', value=dates.faked_end_time(db_event.start_time, db_event.end_time)),
                search.NumberField(name='latitude', value=db_event.latitude),
                search.NumberField(name='longitude', value=db_event.longitude),
                search.TextField(name='categories', value=' '.join(db_event.auto_categories)),
                search.TextField(name='country', value=db_event.country),
            ],
            #language=XX, # We have no good language detection
            rank=int(time.mktime(db_event.start_time.timetuple())),
            )
        return doc_event

class AllEventsIndex(EventsIndex):
    index_name = 'AllEvents'

class FutureEventsIndex(EventsIndex):
    index_name = 'FutureEvents'

    @classmethod
    def _get_query_params_for_indexing(cls):
        return [eventdata.DBEvent.search_time_period==dates.TIME_FUTURE]

def update_fulltext_search_index_batch(events_to_update):
    future_events_to_update = []
    future_events_to_deindex = []
    for db_event in events_to_update:
        if db_event.search_time_period == dates.TIME_FUTURE:
            future_events_to_update.append(db_event)
        else:
            future_events_to_deindex.append(db_event.fb_event_id)

    FutureEventsIndex.update_index(future_events_to_update)
    FutureEventsIndex.delete_ids(future_events_to_deindex)
    AllEventsIndex.update_index(events_to_update)

def delete_from_fulltext_search_index(db_event_id):
    logging.info("Deleting event from search index: %s", db_event_id)
    FutureEventsIndex.delete_ids([db_event_id])
    AllEventsIndex.delete_ids([db_event_id])

def construct_fulltext_search_index(index_future=True):
    if index_future:
        FutureEventsIndex.rebuild_from_query()
    else:
        AllEventsIndex.rebuild_from_query()

