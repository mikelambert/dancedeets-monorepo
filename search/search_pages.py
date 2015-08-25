import logging
import re
import time

from google.appengine.api import search

from loc import gmaps_api
from loc import math
from nlp import categories
from . import search_source

class PageResult(object):
    def __init__(self, result):
        self.id = result.doc_id
        self.name = result.field('name').value
        self.like_count = result.field('like_count').value

class SearchPageQuery(object):
    def __init__(self, bounds=None, min_likes=None, keywords=None):
        self.min_likes = min_likes
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
        # min_likes=query.min_likes,
        self = cls(bounds=bounds, keywords=query.keywords)
        return self

    def _get_candidate_doc_events(self, ids_only=True):
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
        if self.keywords:
            clauses += ['(%s)' % self.keywords]
        if self.min_likes:
            clauses += ['like_count > %d' % self.min_likes]
        if clauses:
            full_search = ' '.join(clauses)
            logging.info("Doing search for %r", full_search)
            #TODO(lambert): implement pagination
            if ids_only:
                options = {'returned_fields': []}
            else:
                options = {'returned_fields': self.extra_fields}
            options = search.QueryOptions(limit=self.limit, **options)
            query = search.Query(query_string=full_search, options=options)
            doc_search_results = search_source.SourceIndex.search(query)
            return doc_search_results.results
        return []

    def get_search_results(self, fbl, prefilter=None, full_event=False):
        a = time.time()
        # Do datastore filtering
        doc_events = self._get_candidate_doc_events(ids_only=False)
        logging.info("Search returned %s pages in %s seconds", len(doc_events), time.time() - a)

        if prefilter:
            doc_events = [x for x in doc_events if prefilter(x)]

        a = time.time()
        results = [PageResult(x) for x in doc_events]

        logging.info("Loading DBEvents took %s seconds", time.time() - a)

        # Now sort and return the results
        a = time.time()
        results.sort(key=lambda x: x.like_count)
        logging.info("search result sorting took %s seconds", time.time() - a)
        return results
