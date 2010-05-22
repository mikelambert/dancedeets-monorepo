#!/usr/bin/env python

from events import eventdata
from events import tags
import base_servlet

class SearchResult(object):
    def __init__(self, fb_user_id, db_event, fb_event, query):
        self.fb_user_id = fb_user_id
        self.db_event = db_event
        self.fb_event = fb_event
        self.query = query

    def get_image(self):
        return eventdata.get_event_image_url(self.fb_event['picture'], eventdata.EVENT_IMAGE_MEDIUM)

    def get_attendence(self):
        return eventdata.get_attendence_for_fb_event(self.fb_event, self.fb_user_id)

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

    def matches_event(self, event, fb_event):
        matches = set()
        if self.any_tags:
            if self.any_tags.intersection(event.tags):
                matches.add(SearchQuery.MATCH_TAGS)
            else:
                return []
        if self.start_time:
            #TODO(lambert): convert these both to times and make the comparisons work
            if self.start_time < fb_event.end_time:
                matches.add(SearchQuery.MATCH_TIME)
            else:
                return []
        if self.end_time:
            if fb_event.start_time < self.end_time:
                matches.add(SearchQuery.MATCH_TIME)
            else:
                return []
        if self.query_args:
            found_keyword = False
            for keyword in self.query_args:
                if keyword in fb_event.name or keyword in fb_event.description:
                    found_keyword = True
            if found_keyword:
                matches.add(SearchQuery.MATCH_QUERY)
            else:
                return []

        return matches
    
    def get_candidate_events(self):
        return eventdata.DBEvent.all().fetch(100)

    def get_search_results(self, facebook):
        # TODO(lambert): implement searching in the appengine backend
        # hard to do inequality search on location *and* time in appengine
        # keyword searching is inefficient in appengine

        # So we either;
        # - use prebucketed time/locations (by latlong grid, buckets of time)
        # - switch to non-appengine like SimpleDB or MySQL on Amazon

        db_events = self.get_candidate_events()
        batch_lookup = base_servlet.BatchLookup(facebook)
        for x in db_events:
            batch_lookup.lookup_event(x.fb_event_id)
        batch_lookup.finish_loading()
        search_results = [SearchResult(facebook.uid, x, batch_lookup.events[x.fb_event_id], self) for x in db_events if self.matches_event(x, batch_lookup.events[x.fb_event_id])]
        return search_results

class SearchHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        self.display['types'] = tags.TYPES
        self.display['styles'] = tags.STYLES

        self.render_template('search')

    def post(self):
        self.finish_preload()
        tags_set = self.request.get_all('tag')
        query = SearchQuery(any_tags=tags_set)
        search_results = query.get_search_results(self.facebook)
        self.display['results'] = search_results
        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        self.render_template('results')

