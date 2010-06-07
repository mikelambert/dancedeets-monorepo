#!/usr/bin/env python

import datetime
import re
import time

from google.appengine.api.labs import taskqueue

import base_servlet
from events import eventdata
from events import tags
from events import users
import facebook
import fb_api
import locations
import smemcache

PREFETCH_EVENTS_INTERVAL = 24 * 60 * 60
assert smemcache.MEMCACHE_EXPIRY >= PREFETCH_EVENTS_INTERVAL

class RsvpAjaxHandler(base_servlet.BaseRequestHandler):
    valid_rsvp = ['attending', 'maybe', 'declined']


    def post(self):
        self.finish_preload()
        event_id = int(self.request.get('event_id'))
        if not event_id:
            self.add_error('missing event_id')
        if not self.request.get('rsvp') in self.valid_rsvp:
            self.add_error('invalid or missing rsvp')
        self.errors_are_fatal()

        rsvp = self.request.get('rsvp')
        if rsvp == 'maybe':
            rsvp = 'unsure'

        #TODO(lambert): clean up our reliance on private methods
        smemcache.delete(self.batch_lookup._memcache_key((event_id, self.batch_lookup.OBJECT_EVENT_MEMBERS)))
        smemcache.delete(self.batch_lookup._memcache_key((self.fb_uid, self.batch_lookup.OBJECT_USER)))

        self.fb_graph.api_request('method/events.rsvp', args=dict(eid=event_id, rsvp_status=rsvp))

        self.write_json_response(success=True)

    def handle_error_response(self, errors):
        self.write_json_repsonse(success=False, errors=errors)


class ViewHandler(base_servlet.BaseRequestHandler):

    def get(self):
        event_id = int(self.request.get('event_id'))
        self.batch_lookup.lookup_event(event_id)
        self.batch_lookup.lookup_event_members(event_id)
        self.finish_preload()
        if event_id:
            event_info = self.batch_lookup.data_for_event(event_id)
            event_members_info = self.batch_lookup.data_for_event_members(event_id)
            e = event_info['info']
        
            location = eventdata.get_geocoded_location_for_event(event_info)
            self.display['location'] = location

            if location['latlng']:
                e_lat, e_lng = location['latlng']
                user_location = locations.get_geocoded_location(self.user.location)
                my_lat, my_lng = user_location['latlng']
                distance = locations.get_distance(e_lat, e_lng, my_lat, my_lng)
                self.display['distance'] = distance
            else:
                self.display['distance'] = None


            self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
            #TODO(lambert): factor out code
            rsvps_list = self.batch_lookup.data_for_user(self.fb_uid)['rsvp_for_events']
            rsvps = dict((int(x['eid']), x['rsvp_status']) for x in rsvps_list)
            rsvp = rsvps[event_id]
            if rsvp == 'unsure':
                rsvp = 'maybe'
            self.display['attendee_status'] = rsvp


            friend_ids = set(x['id'] for x in self.current_user()['friends']['data'])
            event_friends = {}
            for rsvp in 'attending', 'maybe', 'declined', 'noreply':
                if rsvp in event_info:
                    rsvp_friends = [x for x in event_info[rsvp]['data'] if x['id'] in friend_ids]
                    rsvp_friends = sorted(rsvp_friends, key=lambda x: x['name'])
                    for friend in rsvp_friends:
                        #TODO(lambert): Do we want to pre-resolve/cache all these image names in the server? Or just keep images disabled?
                        friend['pic'] = 'https://graph.facebook.com/%s/picture?access_token=%s' % (friend['id'], self.fb_graph.access_token)
                    event_friends[rsvp] = rsvp_friends

            self.display['fb_event'] = e
            for field in ['start_time', 'end_time']:
                self.display[field] = self.parse_fb_timestamp(e[field])

            self.display['pic'] = eventdata.get_event_image_url(self.batch_lookup.data_for_event(event_id)['picture'], eventdata.EVENT_IMAGE_LARGE)

            db_event = eventdata.get_db_event(event_id)
            tags_set = db_event and set(db_event.tags) or []
            self.display['styles'] = [x[1] for x in tags.STYLES if x[0] in tags_set]
            self.display['freestyle_types'] = [x[1] for x in tags.FREESTYLE_EVENT_LIST if x[0] in tags_set]
            self.display['choreo_types'] = [x[1] for x in tags.CHOREO_EVENT_LIST if x[0] in tags_set]
            self.display['event_friends'] = event_friends

            # template rendering
            self.render_template('view')

            # TODO(lambert): maybe offer a link to message the owner
        else:
            self.response.out.write('Need an event_id. Or go to boo.html to login')

class AddHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        self.display['freestyle_types'] = tags.FREESTYLE_EVENT_LIST
        self.display['choreo_types'] = tags.CHOREO_EVENT_LIST
        self.display['styles'] = tags.STYLES

        results_json = self.batch_lookup.data_for_user(self.fb_uid)['all_event_info']
        events = sorted(results_json, key=lambda x: x['start_time'])

        event_ids = [x['eid'] for x in events]
        db_events = []
        MAX_IN_SIZE = 30
        for i in range(0, len(event_ids), MAX_IN_SIZE):
            event_ids_str = ','.join(str(x) for x in event_ids[i:i+MAX_IN_SIZE])
            db_events.extend(eventdata.DBEvent.gql('where fb_event_id in (%s)' % event_ids_str))
        loaded_fb_event_ids = set(x.fb_event_id for x in db_events)

        for event in events:
            # rewrite hack necessary for templates (and above code)
            event['id'] = event['eid']
            event['loaded'] = event['id'] in loaded_fb_event_ids
            for field in ['start_time', 'end_time']:
                event[field] = self.localize_timestamp(datetime.datetime.fromtimestamp(event[field]))

        lastadd_key = 'LastAdd.%s' % (self.fb_uid)
        if not smemcache.get(lastadd_key):
            task_size = 20
            for i in range(0, len(events), task_size):
                taskqueue.add(url='/tasks/load_events', params={'user_id': self.fb_uid, 'event_ids': ','.join(str(x['id']) for x in events[i:i+task_size])})
            smemcache.set(lastadd_key, True, PREFETCH_EVENTS_INTERVAL)

        self.display['events'] = events

        self.render_template('add')

    def post(self):
        if self.request.get('event_id'):
            event_id = int(self.request.get('event_id'))
        elif self.request.get('event_url'):
            url = self.request.get('event_url')
            if '#' in url:
                url = url.split('#')[1]
            match = re.search('eid=(\d+)', url)
            if not match:
                self.add_error('invalid event_url, expecting eid= parameter')
            event_id = int(match.group(1))
        else:
            self.add_error('missing event_url or event_id parameter')

        self.batch_lookup.lookup_event(event_id)
        try:
            self.finish_preload()
        except fb_api.FacebookException, e:
            self.add_error(str(e))

        self.errors_are_fatal()
        e = eventdata.get_db_event(event_id)
        if not e:
            e = eventdata.DBEvent(fb_event_id=event_id)
            e.make_findable_for(self.batch_lookup.data_for_event(event_id))
        e.tags = self.request.get_all('tag')
        e.put()

        self.response.out.write('Thanks for submitting!<br>\n')
        self.response.out.write('<a href="/events/view?event_id=%s">View Page</a>' % event_id)
