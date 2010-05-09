#!/usr/bin/env python

import datetime
import re
import sys

import pytz

import wsgiref.handlers
from facebook import webappfb
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
import gmaps
from events import eventdata
from events import tags
from events import users
from util import text

DEBUG = True

#TODO(lambert): force login before accessing stuff
#TODO(lambert): show event info, queries without login?? P2

#TODO(lambert): add rsvp buttons to the event pages.

#TODO(lambert): allow users to specify what their tags/location/mail-preferences are
#TODO(lambert): send weekly emails with upcoming events per person
#TODO(lambert): send notifications to interested users when someone adds a new event?

#TODO(lambert): add a bunch of events to the db, then dump the db for saving it
#TODO(lambert): support filters on events (by distance? by tags? what else?)

# TODO: move these to a base-servlet module
def import_template_module(template_name):
    try:
        return sys.modules[template_name]
    except KeyError:
        __import__(template_name, globals(), locals(), [])
        return sys.modules[template_name]

def import_template_class(template_name):
    template_module = import_template_module(template_name)
    classname = template_name.split('.')[-1]
    return getattr(template_module, classname)

class BaseRequestHandler(webappfb.FacebookRequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseRequestHandler, self).__init__(*args, **kwargs)
        self.display = {}

    def render_template(self, name):
        template_class = import_template_class(name)
        template = template_class(search_list=[self.display], default_filter=text.html_escape)
        self.response.out.write(template.main().strip())



class MainHandler(BaseRequestHandler):

    def get(self):
        if self.request.get('event_id'):
            e = eventdata.FacebookEvent(self.facebook, int(self.request.get('event_id')))

            e_lat = e.get_location()['lat']
            e_lng = e.get_location()['lng']
            # make sure our cookies are keyed by user-id somehow so different users don't conflict
            my_lat = 37.763506
            my_lng = -122.418144
            distance = gmaps.get_distance(e_lat, e_lng, my_lat, my_lng)

            venue = e.get_fb_event_info()['venue']
            venue = '%s, %s, %s, %s' % (venue['street'], venue['city'], venue['state'], venue['country'])

            # This fails a lot. Split into separate requests? Cache heavily? Make ajax with long timeouts? :(
            try:
                event_friends = e.get_fb_event_friends()
            except urlfetch.DownloadError, exc:
                event_friends = {}
            for rsvp in 'attending', 'unsure', 'declined', 'not_replied':
                if rsvp in event_friends:
                    event_friends[rsvp] = sorted(event_friends[rsvp], key=lambda x: x['name'])
                    for friend in event_friends[rsvp]:
                        friend['name'].encode('utf8')

            self.display = {}
            self.display['event'] = e
            self.display['fb_event'] = e.get_fb_event_info()
            time_offset = users.get_timezone_for_user(self.facebook)
            td = datetime.timedelta(hours=time_offset)

            self.display['start_time'] = datetime.datetime.fromtimestamp(int(e.get_fb_event_info()['start_time'])) + td
            self.display['end_time'] = datetime.datetime.fromtimestamp(int(e.get_fb_event_info()['end_time'])) + td
            self.display['distance'] = distance
            self.display['venue'] = venue

            # function
            self.display['format_html'] = text.format_html
            self.display['date_format'] = text.date_format
            self.display['format'] = text.format

            tags_set = set(e.tags())
            self.display['styles'] = [x[1] for x in tags.STYLES if x[0] in tags_set]
            self.display['types'] = [x[1] for x in tags.TYPES if x[0] in tags_set]
            self.display['event_friends'] = event_friends

            # template rendering
            self.render_template('events.templates.display')

            # FBRequest: Cannot invite user to events??
            # Instead let's offer the user to attend/maybe/decline on an event
            # and then we prompt the user for access and set their settings here.
            #self.facebook.events.rsvp(int(self.request.get('event_id')), "unsure")

            # TODO(lambert): maybe offer a link to message the owner
        else:
            self.response.out.write('Need an event_id. Or go to boo.html to login')

class AddHandler(BaseRequestHandler):
    def get(self):
        self.display['types'] = tags.TYPES
        self.display['styles'] = tags.STYLES

        self.render_template('events.templates.add')

    def post(self):
        #if not validated:
        #    self.get()
        match = re.search('eid=(\d+)', self.request.get('event_url'))
        if not match:
            return self.get()
        event_id = int(match.group(1))
        e = eventdata.FacebookEvent(self.facebook, event_id)
        e.set_tags(self.request.get_all('tag'))
        e.save_db_event()
        self.response.out.write('Thanks for submitting!<br>\n')
        self.response.out.write('<a href="/events/view?event_id=%s">View Page</a>' % event_id)
        
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
                matches.append(MATCH_TAGS)
            else:
                return []
        if self.start_time:
            if self.start_time < event.time:
                matches.append(MATCH_TIME)
            else:
                return []
        if self.end_time:
            if event.time < self.end_time:
                matches.append(MATCH_TIME)
            else:
                return []
        if self.query_args:
            found_keyword = False
            for keyword in self.query_args:
                if keyword in self.name or keyword in self.description:
                    found_keyword = True
            if found_keyword:
                matches.append(MATCH_QUERY)
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

class SearchHandler(BaseRequestHandler):
    def get(self):
        self.display['types'] = tags.TYPES
        self.display['styles'] = tags.STYLES

        self.render_template('events.templates.search')

    def post(self):
        #if not validated:
        #    self.get()
        tags_set = self.request.get_all('tag')
        query = SearchQuery(any_tags=tags_set)
        search_results = query.get_search_results(self.facebook)
        self.display['results'] = search_results
        self.display['format_html'] = text.format_html
        self.render_template('events.templates.results')

        
class UserHandler(BaseRequestHandler):
    def get(self):
        self.display['DANCES'] = users.DANCES
        self.display['DANCE_HEADERS'] = users.DANCE_HEADERS
        self.display['DANCE_LISTS'] = users.DANCE_LISTS

        defaults = {
            'zip': '',
            'freestyle': users.FREESTYLE_FAN_NO_CLUBS,
            'choreo': users.CHOREO_FAN,
        }
        fetched_users = users.User.gql('where fb_uid = :fb_uid', fb_uid=self.facebook.uid).fetch(1)
        if fetched_users:
            user = fetched_users[0]
            for k in defaults:
                defaults[k] = getattr(user, k)
        for field in defaults.keys():
            if self.request.get(field):
                defaults[field] = self.request.get(field)
        self.display['defaults'] = defaults

        #print urllib.urlopen('http://graph.facebook.com/me?access_token=%s' % self.facebook.access_token).read()

        self.render_template('events.templates.user')

    def post(self):
        #if not validated:
        #    self.get()
        #TODO(lambert): save the data here
        fetched_users = users.User.gql('where fb_uid = :fb_uid', fb_uid=self.facebook.uid).fetch(1)
        if fetched_users:
            user = fetched_users[0]
        else:
            user = users.User(fb_uid=self.facebook.uid)
        for field in ['zip', 'freestyle', 'choreo']:
            form_value = self.request.get(field)
            setattr(user, field, form_value)
        user.put()
        


URLS = [
    ('/events/view', MainHandler),
    ('/events/add', AddHandler),
    ('/events/search', SearchHandler),
    ('/user/edit', UserHandler),
]

def main():
     application = webapp.WSGIApplication(URLS, debug=DEBUG)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
