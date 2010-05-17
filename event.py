#!/usr/bin/env python

import datetime
import re

from google.appengine.api import urlfetch
import locations
from events import eventdata
from events import tags
import base_servlet

DEBUG = True

#TODO(lambert): add rsvp buttons to the event pages.

class RsvpAjaxHandler(base_servlet.BaseRequestHandler):
    valid_rsvp = ['attending', 'maybe', 'declined']

    def validate_form_for_errors(self):
        errors = []
        if not self.request.get('event_id'):
            errors.append('missing event_id')
        if not self.request.get('rsvp') in valid_rsvp:
            errors.append("invalid or missing rsvp')
        return errors

    def post(self):
        self.finish_preload()
        if self.is_valid_form():
            rsvp = self.request.get('rsvp')
            if rsvp == 'maybe': #TODO(lambert): do this in the validation framework?
                rsvp = 'unsure'

            self.facebook.events.rsvp(int(self.request.get('event_id')), rsvp)
        #TODO(lambert): write out success/failure error code and json response
        self.response.out.write('OK')


class MainHandler(base_servlet.BaseRequestHandler):

    def get(self):
        event_id = int(self.request.get('event_id'))
        self.batch_lookup.lookup_event(event_id)
        self.finish_preload()
        if event_id:
            e = self.batch_lookup.events[event_id]['info']
        
            location = eventdata.get_geocoded_location_for_event(e)
            self.display['location'] = location

            e_lat = location['lat']
            e_lng = location['lng']
            # make sure our cookies are keyed by user-id somehow so different users don't conflict
            my_lat = 37.763506
            my_lng = -122.418144
            distance = locations.get_distance(e_lat, e_lng, my_lat, my_lng)

            #TODO(lambert): properly handle venue vs street/city/state/country and location to get authoritative info
            venue = e['venue']
            venue = '%s, %s, %s, %s' % (venue['street'], venue['city'], venue['state'], venue['country'])

            friend_ids = set(x['id'] for x in self.current_user()['friends']['data'])
            event_friends = {}
            event_info = self.batch_lookup.events[event_id]
            for rsvp in 'attending', 'maybe', 'declined', 'noreply':
                if rsvp in event_info:
                    rsvp_friends = [x for x in event_info[rsvp]['data'] if x['id'] in friend_ids]
                    rsvp_friends = sorted(rsvp_friends, key=lambda x: x['name'])
                    for friend in rsvp_friends:
                        #TODO(lambert): Do we want to pre-resolve/cache all these image names in the server? Or just keep images disabled?
                        friend['pic'] = 'https://graph.facebook.com/%s/picture?access_token=%s' % (friend['id'], self.facebook.access_token)
                    event_friends[rsvp] = rsvp_friends

            self.display['fb_event'] = e
            for field in ['start_time', 'end_time']:
                self.display[field] = self.localize_timestamp(datetime.datetime.strptime(e[field], '%Y-%m-%dT%H:%M:%S+0000'))
            self.display['distance'] = distance
            self.display['venue'] = venue

            self.display['pic'] = eventdata.get_event_image_url(self.batch_lookup.events[event_id]['picture'], eventdata.EVENT_IMAGE_LARGE)

            db_event = eventdata.get_db_event(event_id)
            tags_set = db_event and set(db_event.tags) or []
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

    def validate_form_for_errors(self):
        errors = []
        if not self.request.get('event_url') and not self.request.get('event_id'):
            errors.append('missing event_url or event_id')
    
        match = re.search('eid=(\d+)', self.request.get('event_url'))
        if not match:
            errors.append('invalid event_url, expecting eid= parameter')
        return errors
    def post(self):
        self.finish_preload()
        if not self.is_form_valid():
            return self.get()
        event_id = None
        if self.request.get('event_url'):
            match = re.search('eid=(\d+)', self.request.get('event_url'))
            event_id = int(match.group(1))
        if self.request.get('event_id'):
            event_id = int(self.request.get('event_id'))
        assert event_id # How can this happend??

        e = eventdata.get_db_event(event_id)
        e.tags = self.request.get_all('tag')
        e.put()

        self.response.out.write('Thanks for submitting!<br>\n')
        self.response.out.write('<a href="/events/view?event_id=%s">View Page</a>' % event_id)
