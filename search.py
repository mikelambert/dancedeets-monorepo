#!/usr/bin/env python

from events import eventdata
from events import tags
import base_servlet

#TODO(lambert): add rsvp buttons to the search results.
#TODO(lambert): support filters on events (by distance? by tags? what else?)

CHOOSE_RSVPS = ['attending', 'maybe', 'declined']

class SearchResult(object):
    def __init__(self, fb_user_id, db_event, fb_event, query):
        self.fb_user_id = fb_user_id
        # TODO(lambert): clean up these three params
        self.event = db_event
        self.real_event = fb_event
        self.fb_event = fb_event['info']
        self.query = query

    def get_image(self):
        #TODO(lambert): reimplement event photos in the small form...
        return ''
        #return eventdata.get_event_image_url(self.fb_event['picture'], eventdata.EVENT_IMAGE_MEDIUM)

    def get_attendence(self):
        for rsvp in CHOOSE_RSVPS:
            if [x for x in self.real_event[rsvp]['data'] if int(x['id']) == self.fb_user_id]:
                return rsvp
        return 'noreply'

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
            if self.any_tags.intersection(event.tags):
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

        # TODO(lambert): Clean up our use of eventdata.FacebookEvent in light of our preloading API
        db_events = eventdata.DBEvent.all().fetch(100)
        batch_lookup = base_servlet.BatchLookup(facebook)
        for x in db_events:
            batch_lookup.lookup_event(x.fb_event_id)
        batch_lookup.finish_loading()
        #TODO(lambert): need to pass facebook so they can get at the image urls
        search_results = [SearchResult(facebook.uid, x, batch_lookup.events[x.fb_event_id], self) for x in db_events if self.matches_event(x)]
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
        self.display['CHOOSE_RSVPS'] = CHOOSE_RSVPS
        self.render_template('events.templates.results')

