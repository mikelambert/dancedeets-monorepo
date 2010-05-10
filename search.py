#!/usr/bin/env python

from events import eventdata
from events import tags
import base_servlet

#TODO(lambert): add rsvp buttons to the search results.
#TODO(lambert): support filters on events (by distance? by tags? what else?)

class SearchResult(object):
    def __init__(self, event, query):
        self.event = event
        self.query = query

class SearchQuery(object):
    MATCH_TAGS = 'TAGS'
    MATCH_TIME = 'TIME'
    MATCH_LOCATION = 'LOCATION'
    MATCH_QUERY = 'QUERY'

    def __init__(self, any_tags=None, start_time=None, end_time=None, location=None, distance=None, query_args=None):
        self.any_tags = set(any_tags)
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.distance = distance
        self.query_args = query_args

    def matches_event(self, event):
        matches = set()
        if self.any_tags:
            if self.any_tags.intersection(event.tags()):
                matches.add(SearchQuery.MATCH_TAGS)
            else:
                return []
        if self.start_time:
            if self.start_time < event.time:
                matches.add(SearchQuery.MATCH_TIME)
            else:
                return []
        if self.end_time:
            if event.time < self.end_time:
                matches.add(SearchQuery.MATCH_TIME)
            else:
                return []
        if self.query_args:
            found_keyword = False
            for keyword in self.query_args:
                if keyword in self.name or keyword in self.description:
                    found_keyword = True
            if found_keyword:
                matches.add(SearchQuery.MATCH_QUERY)
            else:
                return []

        return matches

    def get_search_results(self, facebook):
        # TODO(lambert): implement searching in the appengine backend
        # hard to do inequality search on location *and* time in appengine
        # keyword searching is inefficient in appengine

        # So we either;
        # - use prebucketed time/locations (by latlong grid, buckets of time)
        # - switch to non-appengine like SimpleDB or MySQL on Amazon

        fb_events = [eventdata.FacebookEvent(facebook, x.fb_event_id) for x in eventdata.DBEvent.all().fetch(100)]
        search_results = [SearchResult(x, self) for x in fb_events if self.matches_event(x)]
        return search_results

class SearchHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        self.display['types'] = tags.TYPES
        self.display['styles'] = tags.STYLES

        self.render_template('events.templates.search')

    def post(self):
        self.finish_preload()
        #if not validated:
        #    self.get()
        tags_set = self.request.get_all('tag')
        query = SearchQuery(any_tags=tags_set)
        search_results = query.get_search_results(self.facebook)
        self.display['results'] = search_results
        self.render_template('events.templates.results')

