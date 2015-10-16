#!/usr/bin/env python

import datetime
import logging
import re
import time

from google.appengine.api import search

from loc import gmaps_api
from loc import math
from nlp import categories
from search import index
from search import search_base
from . import class_models


# StudioClass Models:
# scrapy.Item (optional)
# ndb.Model
# search.Document
# (eventually, json representation?)

def build_display_event_dict(doc):
    def get(x):
        return doc.field(x).value
    data = {
        'name': get('name'),
        'image': None,
        'cover': None,
        'start_time': get('start_time'),
        'end_time': get('end_time'),
        'location': "", #TODO: Add Location
        'lat': get('latitude'),
        'lng': get('longitude'),
        'attendee_count': None,
        'categories': get('categories').split(' '),
        'keywords': None,
    }
    return data


class ClassSearchQuery(object):
    #TODO: remove duplicated code that's shared between this and search.SearchQuery. Most notably:
    #__init__, create_from_form, and _get_query_string
    def __init__(self, time_period=None, start_date=None, end_date=None, bounds=None, min_attendees=None, keywords=None):
        self.time_period = time_period

        self.start_date = start_date
        self.end_date = end_date
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
        if self.keywords:
            clauses += ['(%s)' % self.keywords]
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
        query = search.Query(query_string=query_string)
        doc_search_results = doc_index.search(query)
        return doc_search_results.results

    def get_search_results(self, fbl, prefilter=None, full_event=False):
        a = time.time()
        # Do datastore filtering
        doc_events = self._get_candidate_doc_events(ids_only=not prefilter)
        logging.info("Search returned %s events in %s seconds", len(doc_events), time.time() - a)

        # ...and do filtering based on the contents inside our app
        a = time.time()
        search_results = [search_base.SearchResult(x.doc_id, build_display_event_dict(x)) for x in doc_events]
        logging.info("SearchResult construction took %s seconds, giving %s results", time.time() - a, len(search_results))
    
        search_results = self._deduped_results(search_results)

        # Now sort and return the results
        search_results.sort(key=lambda x: x.start_time)
        return search_results


class StudioClassIndex(index.BaseIndex):
    index_name = 'StudioClassIndex'
    obj_type = class_models.StudioClass

    @classmethod
    def _get_query_params_for_indexing(cls):
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        return [(class_models.StudioClass.start_time >= yesterday)]

    @classmethod
    def _create_doc_event(cls, studio_class):
        title = '%s: %s' % (studio_class.style, studio_class.teacher)
        description = studio_class.teacher_link
        # include twitter link to studio?
        doc_event = search.Document(
            doc_id=studio_class.key.string_id(),
            fields=[
                search.TextField(name='name', value=title),
                search.TextField(name='studio', value=studio_class.studio_name),
                search.TextField(name='description', value=description),
                search.DateField(name='start_time', value=studio_class.start_time),
                search.DateField(name='end_time', value=studio_class.end_time),
                search.NumberField(name='latitude', value=studio_class.latitude),
                search.NumberField(name='longitude', value=studio_class.longitude),
                search.TextField(name='categories', value=' '.join(studio_class.auto_categories)),
                #search.TextField(name='country', value=studio_class.country),
            ],
            #language=XX, # We have no good language detection
            rank=int(time.mktime(studio_class.start_time.timetuple())),
            )
        return doc_event
