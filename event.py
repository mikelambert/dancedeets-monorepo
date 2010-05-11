#!/usr/bin/env python

import datetime
import re

from google.appengine.api import urlfetch
import gmaps
from events import eventdata
from events import tags
import base_servlet

DEBUG = True

#TODO(lambert): add rsvp buttons to the event pages.

class RsvpAjaxHandler(base_servlet.BaseRequestHandler):
    def post(self):
        self.finish_preload()
        if self.request.get('event_id'):
            rsvp = self.request.get('rsvp')
            valid_rsvp = ['attending', 'maybe', 'declined']
            assert rsvp in valid_rsvp #TODO(lambert): validation
            if rsvp == 'maybe':
                rsvp = 'unsure'

            self.facebook.events.rsvp(int(self.request.get('event_id')), rsvp)
        #TODO(lambert): write out success/failure error code and json response
        self.response.out.write('OK')


class MainHandler(base_servlet.BaseRequestHandler):

    def get(self):
        self.finish_preload()
        if self.request.get('event_id'):
            e = eventdata.FacebookEvent(self.facebook, int(self.request.get('event_id')))
        
            e_lat = e.get_location()['lat']
            e_lng = e.get_location()['lng']
            # make sure our cookies are keyed by user-id somehow so different users don't conflict
            my_lat = 37.763506
            my_lng = -122.418144
            distance = gmaps.get_distance(e_lat, e_lng, my_lat, my_lng)

            #TODO(lambert): properly handle venue vs street/city/state/country and location to get authoritative info
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

            self.display['event'] = e
            self.display['fb_event'] = e.get_fb_event_info()
            for field in ['start_time', 'end_time']:
                self.display[field] = self.localize_timestamp(datetime.datetime.fromtimestamp(int(e.get_fb_event_info()[field])))
            self.display['distance'] = distance
            self.display['venue'] = venue


            tags_set = set(e.tags())
            self.display['styles'] = [x[1] for x in tags.STYLES if x[0] in tags_set]
            self.display['types'] = [x[1] for x in tags.TYPES if x[0] in tags_set]
            self.display['event_friends'] = event_friends

            # template rendering
            self.render_template('events.templates.display')

            # TODO(lambert): maybe offer a link to message the owner
        else:
            self.response.out.write('Need an event_id. Or go to boo.html to login')

class AddHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        self.display['types'] = tags.TYPES
        self.display['styles'] = tags.STYLES

        results_json = self.batch_lookup.users[self.facebook.uid]['events']
        events = sorted(results_json['data'], key=lambda x: x['start_time'])
        for event in events:
            for field in ['start_time', 'end_time']:
                event[field] = self.localize_timestamp(datetime.datetime.strptime(event[field], '%Y-%m-%dT%H:%M:%S+0000'))

        self.display['events'] = events

        self.render_template('events.templates.add')

    def post(self):
        self.finish_preload()
        #if not validated:
        #    self.get()
        event_id = None
        #TODO: validation
        assert not (self.request.get('event_url') and self.request.get('event_id'))
        if self.request.get('event_url'):
            match = re.search('eid=(\d+)', self.request.get('event_url'))
            if not match: # TODO(lambert): poor man's validation??
                return self.get()
            event_id = int(match.group(1))
        if self.request.get('event_id'):
            event_id = int(self.request.get('event_id'))
        if not event_id:
            assert False # TODO: validation

        e = eventdata.FacebookEvent(self.facebook, event_id)
        e.set_tags(self.request.get_all('tag'))
        e.save_db_event()
        self.response.out.write('Thanks for submitting!<br>\n')
        self.response.out.write('<a href="/events/view?event_id=%s">View Page</a>' % event_id)
