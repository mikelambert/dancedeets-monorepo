#!/usr/bin/env python

import collections
import datetime
import logging
import pprint
import time

from google.appengine.ext import ndb
from google.appengine.api import search

from events import eventdata
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
        else:
            return db_event.has_content()

    @classmethod
    def build(cls, db_event):
        """Save off the minimal set of data necessary to render an event on the list page, for quicker loading/serialization from memcache/db."""
        if not cls.can_build_from(db_event):
            return None
        try:
            display_event = cls(id=db_event.fb_event_id)
            # The event_keywords are actually _BaseValue objects, not strings.
            # So they fail json serialization, and must be converted manually here.
            keywords = [unicode(x) for x in db_event.event_keywords]
            categories = [unicode(x) for x in db_event.auto_categories]
            display_event.data = {
                'name': db_event.name,
                'image': db_event.image_url,
                'cover': db_event.largest_cover,
                'start_time': db_event.fb_event['info']['start_time'],
                'end_time': db_event.fb_event['info'].get('end_time'),
                'location': db_event.actual_city_name,
                'lat': db_event.latitude, # used for de-duping events
                'lng': db_event.longitude, # used for de-duping events
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


class Search(object):
    DATE_SEARCH_FORMAT = '%Y-%m-%d'

    def __init__(self, search_query):
        self.query = search_query
        self.limit = 1000
        # Extra search index fields to return
        self.extra_fields = []

    def _get_query_string(self):
        clauses = []
        if self.query.bounds:
            # We try to keep searches as simple as possible,
            # using just AND queries on latitude/longitude.
            # But for stuff crossing +/-180 degrees,
            # we need to do an OR longitude query on each side.
            latitudes = (self.query.bounds[0][0], self.query.bounds[1][0])
            longitudes = (self.query.bounds[0][1], self.query.bounds[1][1])
            clauses += ['latitude >= %s AND latitude <= %s' % latitudes]
            if longitudes[0] < longitudes[1]:
                clauses += ['longitude >= %s AND longitude <= %s' % longitudes]
            else:
                clauses += ['(longitude >= %s OR longitude <= %s)' % longitudes]
        if self.query.start_date:
            clauses += ['end_time >= %s' % self.query.start_date.strftime(self.DATE_SEARCH_FORMAT)]
        if self.query.end_date:
            clauses += ['start_time <= %s' % self.query.end_date.strftime(self.DATE_SEARCH_FORMAT)]
        if self.query.keywords:
            clauses += ['(%s)' % self.query.keywords]
        if self.query.min_attendees:
            clauses += ['attendee_count > %d' % self.query.min_attendees]
        if clauses:
            return ' '.join(clauses)
        else:
            return None

    def _get_candidate_doc_events(self, ids_only=True):
        query_string = self._get_query_string()
        if not query_string:
            return []

        search_index = AllEventsIndex
        if self.query.time_period:
            if self.query.time_period in search_base.FUTURE_INDEX_TIMES:
                search_index = FutureEventsIndex
        if self.query.start_date:
            # Do we want/need this hack?
            if self.query.start_date > datetime.date.today():
                search_index = FutureEventsIndex

        logging.info("Doing search for %r", query_string)
        doc_index = search_index.real_index()
        #TODO(lambert): implement pagination
        if ids_only:
            options = {'returned_fields': ['start_time', 'end_time'] + self.extra_fields}
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
        if self.query.time_period == search_base.TIME_ONGOING:
            doc_events = [x for x in doc_events if x.field('start_time').value < now]
        elif self.query.time_period == search_base.TIME_UPCOMING:
            doc_events = [x for x in doc_events if x.field('start_time').value > now]
        elif self.query.time_period == search_base.TIME_PAST:
            doc_events = [x for x in doc_events if x.field('end_time').value < now]
        elif self.query.time_period == search_base.TIME_ALL_FUTURE:
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
        if not db_event.has_content():
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
                search.TextField(name='name', value=db_event.name),
                search.TextField(name='description', value=db_event.description),
                search.NumberField(name='attendee_count', value=db_event.attendee_count or 0),
                search.DateField(name='start_time', value=db_event.start_time),
                search.DateField(name='end_time', value=dates.faked_end_time(db_event.start_time, db_event.end_time)),
                search.NumberField(name='latitude', value=db_event.latitude),
                search.NumberField(name='longitude', value=db_event.longitude),
                search.TextField(name='categories', value=' '.join(db_event.auto_categories)),
                search.TextField(name='country', value=db_event.country),
                # Use NumberField instead of DateField since we care about hours/minutes/seconds,
                # which are otherwise discarded with a DateField.
                # We want this to know what events have been added in the last 24 hours,
                # so we can promote them to users when we send out daily notifications.
                search.NumberField(name='creation_time', value=int(time.mktime(db_event.creation_time.timetuple())) if db_event.creation_time else 0),
            ],
            # language=XX, # We have no good language detection
            rank=int(time.mktime(db_event.start_time.timetuple())),
        )
        return doc_event


class AllEventsIndex(EventsIndex):
    index_name = 'AllEvents'


class FutureEventsIndex(EventsIndex):
    index_name = 'FutureEvents'

    @classmethod
    def _get_query_params_for_indexing(cls):
        return [eventdata.DBEvent.search_time_period == dates.TIME_FUTURE]


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
        index = FutureEventsIndex
    else:
        index = AllEventsIndex
    index.rebuild_from_query(force=True)
