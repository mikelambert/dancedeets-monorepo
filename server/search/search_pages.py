import logging
import time

from google.appengine.api import search

from event_scraper import thing_db
from . import search_source

class PageResult(object):
    def __init__(self, result, source):
        self.id = result.doc_id
        self.name = result.field('name').value
        self.like_count = result.field('like_count').value
        self.category = result.field('category').value
        self.category_list = result.field('category_list').value
        self.num_real_events = result.field('num_real_events').value
        self.source = source

class SearchPages(object):
    def __init__(self, search_query):
        self.query = search_query
        self.limit = 1000
        # Extra search index fields to return
        self.extra_fields = []

    def _get_candidate_doc_events(self, ids_only=True):
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
        if self.query.keywords:
            clauses += ['(%s)' % self.query.keywords]
        if self.query.min_likes:
            clauses += ['like_count > %d' % self.query.min_likes]
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

    def get_search_results(self, prefilter=None, full_event=False):
        a = time.time()
        # Do datastore filtering
        doc_events = self._get_candidate_doc_events(ids_only=False)
        logging.info("Search returned %s pages in %s seconds", len(doc_events), time.time() - a)

        if prefilter:
            doc_events = [x for x in doc_events if prefilter(x)]

        real_sources = thing_db.Source.get_by_key_name([x.doc_id for x in doc_events])

        a = time.time()
        results = [PageResult(doc, source) for doc, source in zip(doc_events, real_sources)]

        logging.info("Loading DBEvents took %s seconds", time.time() - a)

        # Now sort and return the results
        a = time.time()
        results.sort(key=lambda x: x.like_count)
        logging.info("search result sorting took %s seconds", time.time() - a)
        return results
