#!/usr/bin/env python

import datetime
import logging
import time

from google.appengine.api import search

from loc import gmaps_api
from loc import math
from search import index
from search import search_base
from . import class_models

# StudioClass Models:
# scrapy.Item (optional)
# ndb.Model
# search.Document
# (eventually, json representation?)

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def build_display_event_dict(doc):
    def get(x):
        try:
            return doc.field(x).value
        except ValueError:
            return None

    data = {
        'name': get('name'),
        'image': None,
        'cover': None,
        'start_time': get('start_time').strftime(DATETIME_FORMAT),
        'end_time': get('end_time').strftime(DATETIME_FORMAT),
        'location': get('studio'),
        'lat': get('latitude'),
        'lng': get('longitude'),
        'attendee_count': None,
        'categories': [x for x in get('categories').split(' ') if x],
        'keywords': None,
        # Unique to studio classes:
        'source_page': get('source_page'),
        'sponsor': get('sponsor'),
    }
    return data


class ClassSearch(object):
    def __init__(self, search_query):
        self.query = search_query
        self.limit = search.MAXIMUM_DOCUMENTS_RETURNED_PER_SEARCH  # 1000
        # Extra search index fields to return
        self.extra_fields = []

    DATE_SEARCH_FORMAT = '%Y-%m-%d'

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
            clauses += ['start_time < %s' % self.query.end_date.strftime(self.DATE_SEARCH_FORMAT)]
        if self.query.keywords:
            clauses += ['(%s)' % self.query.keywords]
        if clauses:
            return ' '.join(clauses)
        else:
            return None

    def _get_candidate_doc_events(self):
        query_string = self._get_query_string()
        if not query_string:
            return []
        logging.info("Doing search for %r", query_string)
        doc_index = StudioClassIndex.real_index()
        options = search.QueryOptions(limit=self.limit)
        query = search.Query(query_string=query_string, options=options)
        doc_search_results = doc_index.search(query)
        return doc_search_results.results

    def get_search_results(self):
        a = time.time()
        # Do datastore filtering
        doc_events = self._get_candidate_doc_events()
        logging.info("Search returned %s events in %s seconds", len(doc_events), time.time() - a)

        # ...and do filtering based on the contents inside our app
        a = time.time()
        search_results = [search_base.SearchResult(None, build_display_event_dict(x)) for x in doc_events]
        logging.info("SearchResult construction took %s seconds, giving %s results", time.time() - a, len(search_results))

        # Now sort and return the results
        search_results.sort(key=lambda x: x.start_time)
        return search_results


class StudioClassIndex(index.BaseIndex):
    index_name = 'StudioClassIndex'
    obj_type = class_models.StudioClass
    delete_threshold = 0.40

    @classmethod
    def _get_query_params_for_indexing(cls):
        yesterday = datetime.datetime.combine(datetime.date.today(), datetime.time.min) - datetime.timedelta(days=1)
        return [(class_models.StudioClass.start_time >= yesterday)]

    @classmethod
    def _create_doc_event(cls, studio_class):
        title = '%s: %s' % (studio_class.style, studio_class.teacher)
        description = studio_class.teacher_link
        # include twitter link to studio?
        timestamp = min(int(time.mktime(studio_class.start_time.timetuple())), 2**31 - 1)
        doc_event = search.Document(
            doc_id=studio_class.key.string_id(),
            fields=[
                search.TextField(name='name', value=title),
                search.TextField(name='studio', value=studio_class.studio_name),
                search.TextField(name='source_page', value=studio_class.source_page),
                search.TextField(name='description', value=description),
                search.DateField(name='start_time', value=studio_class.start_time),
                search.DateField(name='end_time', value=studio_class.end_time),
                search.NumberField(name='latitude', value=studio_class.latitude),
                search.NumberField(name='longitude', value=studio_class.longitude),
                search.TextField(name='categories', value=' '.join(studio_class.auto_categories)),
                search.TextField(name='sponsor', value=studio_class.sponsor),
                #search.TextField(name='country', value=studio_class.country),
            ],
            #language=XX, # We have no good language detection
            rank=timestamp,
        )
        return doc_event
