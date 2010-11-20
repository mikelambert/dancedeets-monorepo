#!/usr/bin/env python

import datetime
import logging
import re
import time
import urllib
from django.utils import simplejson

from google.appengine.api.labs import taskqueue

import base_servlet
from events import eventdata
from events import tags
from events import users
from logic import backgrounder
from logic import event_classifier
from logic import potential_events
from logic import rsvp
import facebook
import fb_api
import locations
import smemcache
from util import dates
from util import urls

PREFETCH_EVENTS_INTERVAL = 24 * 60 * 60

class RsvpAjaxHandler(base_servlet.BaseRequestHandler):
    valid_rsvp = ['attending', 'maybe', 'declined']


    def post(self):
        self.finish_preload()
        event_id = self.request.get('event_id')
        if not event_id:
            self.add_error('missing event_id')
        if not self.request.get('rsvp') in self.valid_rsvp:
            self.add_error('invalid or missing rsvp')
        self.errors_are_fatal()

        rsvp_status = self.request.get('rsvp')

        rsvps = rsvp.RSVPManager(self.batch_lookup)
        success = rsvps.set_rsvp_for_event(self.fb_graph, event_id, rsvp_status)

        self.write_json_response(dict(success=success))

    def handle_error_response(self, errors):
        self.write_json_response(dict(success=False, errors=errors))


class RedirectToEventHandler(base_servlet.BaseRequestHandler):

    def requires_login(self):
        return False

    def get(self):
        event_id = self.request.get('event_id')
        if not event_id:
            self.response.out.write('Need an event_id.')
            return

        # Logged in users go directly to the event...
        if self.user:
            self.redirect(urls.raw_fb_event_url(event_id))

        # For everyone else, there's an interstitial.
        self.batch_lookup.lookup_event(event_id)
        self.finish_preload()

        event_info = self.batch_lookup.data_for_event(event_id)
        if event_info['deleted']:
            self.response.out.write('This event was deleted.')
            return

        self.display['event'] = event_info
        self.display['next'] =  self.request.url
        self.render_template('event_interstitial')


class ViewHandler(base_servlet.BaseRequestHandler):

    def get(self):
        event_id = self.request.get('event_id')
        if not event_id:
            self.response.out.write('Need an event_id.')
            return

        db_event = eventdata.DBEvent.get_by_key_name(event_id)
        if not db_event:
            self.response.out.write('This event has not been added')
            return

        self.batch_lookup.lookup_event(event_id)
        #self.batch_lookup.lookup_event_members(event_id)
        self.finish_preload()

        event_info = self.batch_lookup.data_for_event(event_id)
        if event_info['deleted']:
            self.response.out.write('This event was deleted.')
            return

        # Disable event_members stuff while we figure out a better way to background-load this
        try:
            event_members_info = self.batch_lookup.data_for_event_members(event_id)
        except KeyError:
            event_members_info = None
        event_members_info = []
        e = event_info['info']
    
        location = eventdata.get_geocoded_location_for_event(event_info)
        self.display['location'] = location

        if location['latlng'] and self.user.location:
            e_lat, e_lng = location['latlng']
            user_location = locations.get_geocoded_location(self.user.location)
            my_lat, my_lng = user_location['latlng']
            distance = locations.get_distance(e_lat, e_lng, my_lat, my_lng)
            self.display['distance'] = distance
        else:
            self.display['distance'] = None

        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        rsvps = rsvp.RSVPManager(self.batch_lookup)
        self.display['attendee_status'] = rsvps.get_rsvp_for_event(event_id)

        friend_ids = set(x['id'] for x in self.current_user()['friends']['data'])
        event_friends = {}
        for rsvp_status in 'attending', 'maybe', 'declined', 'noreply':
            if rsvp_status in event_members_info:
                rsvp_friends = [x for x in event_members_info[rsvp_status]['data'] if x['id'] in friend_ids]
                rsvp_friends = sorted(rsvp_friends, key=lambda x: x['name'])
                for friend in rsvp_friends:
                    friend['pic'] = 'https://graph.facebook.com/%s/picture?access_token=%s' % (friend['id'], self.fb_graph.access_token)
                event_friends[rsvp_status] = rsvp_friends

        self.display['fb_event'] = e
        for field in ['start_time', 'end_time']:
            self.display[field] = eventdata.parse_fb_timestamp(e[field])

        self.display['pic'] = eventdata.get_event_image_url(self.batch_lookup.data_for_event(event_id)['picture'], eventdata.EVENT_IMAGE_LARGE)

        tags_set = db_event and set(db_event.tags) or []
        self.display['styles'] = [x[1] for x in tags.STYLES if x[0] in tags_set]
        self.display['freestyle_types'] = [x[1] for x in tags.FREESTYLE_EVENT_LIST if x[0] in tags_set]
        self.display['choreo_types'] = [x[1] for x in tags.CHOREO_EVENT_LIST if x[0] in tags_set]
        self.display['event_friends'] = event_friends

        # template rendering
        self.render_template('view')

        # TODO(lambert): maybe offer a link to message the owner

class AdminEditHandler(base_servlet.BaseRequestHandler):
    def get(self):
        event_id = None
        if self.request.get('event_url'):
            event_id = get_id_from_url(self.request.get('event_url'))
        elif self.request.get('event_id'):
            event_id = self.request.get('event_id')
        self.batch_lookup.lookup_event(event_id)
        self.finish_preload()

        fb_event = self.batch_lookup.data_for_event(event_id)
        if fb_event['info']['privacy'] != 'OPEN':
            self.add_error('Cannot add secret/closed events to dancedeets!')

        self.errors_are_fatal()

        # Don't insert object until we're ready to save it...
        e = eventdata.DBEvent.get_by_key_name(event_id) or eventdata.DBEvent()
        if e.creating_fb_uid:
            f = urllib.urlopen('https://graph.facebook.com/%s?access_token=%s' % (e.creating_fb_uid, self.fb_graph.access_token))
            json = simplejson.loads(f.read())
            creating_user = json['name']
        else:
            creating_user = None

        original_address = eventdata.get_original_address_for_event(fb_event)
        geocoded_address = locations.get_geocoded_location(original_address)['address']
        remapped_address = eventdata.get_remapped_address_for(original_address)

        self.display['creating_user'] = creating_user
        self.display['original_address'] = original_address
        self.display['geocoded_address'] = geocoded_address
        self.display['remapped_address'] = remapped_address

        self.display['freestyle_types'] = tags.FREESTYLE_EVENT_LIST
        self.display['choreo_types'] = tags.CHOREO_EVENT_LIST
        self.display['styles'] = tags.STYLES

        self.display['event'] = e
        self.display['fb_event'] = fb_event

        self.render_template('admin_edit')

    def post(self):
        event_id = self.request.get('event_id')
        self.batch_lookup.lookup_event(event_id)
        try:
            self.finish_preload()
        except fb_api.FacebookException, e:
            self.add_error(str(e))

        fb_event = self.batch_lookup.data_for_event(event_id)
        if fb_event['info']['privacy'] != 'OPEN':
            self.add_error('Cannot add secret/closed events to dancedeets!')

        self.errors_are_fatal()


        original_address = eventdata.get_original_address_for_event(fb_event)
        remapped_address = eventdata.get_remapped_address_for(original_address)

        new_remapped_address = self.request.get('remapped_address')
        if new_remapped_address != remapped_address:
            eventdata.save_remapped_address_for(original_address, new_remapped_address)

        e = eventdata.DBEvent.get_or_insert(event_id)
        e.tags = self.request.get_all('tag')
        e.creating_fb_uid = self.user.fb_uid
        e.creation_time = datetime.datetime.now()
        e.make_findable_for(self.batch_lookup.data_for_event(event_id))
        e.put()

        self.user.add_message("Changes saved!")
        self.redirect('/events/admin_edit?event_id=%s' % event_id)

def get_id_from_url(url):
    if '#' in url:
        url = url.split('#')[1]
    match = re.search('eid=(\d+)', url)
    if not match:
        return None
    return match.group(1)

class AddHandler(base_servlet.BaseRequestHandler):
    def get(self):

        self.display['freestyle_types'] = tags.FREESTYLE_EVENT_LIST
        self.display['choreo_types'] = tags.CHOREO_EVENT_LIST
        self.display['styles'] = tags.STYLES

        fb_event = None
        events = []

        if self.request.get('event_url'):
            event_id = get_id_from_url(self.request.get('event_url'))
        else:
            event_id = self.request.get('event_id')
        if event_id:
            self.batch_lookup.lookup_event(event_id)
            self.finish_preload()
            fb_event = self.batch_lookup.data_for_event(event_id)
        else:
            self.finish_preload()
            results_json = self.batch_lookup.data_for_user(self.fb_uid)['all_event_info']
            events = sorted(results_json, key=lambda x: x['start_time'])

            db_events = eventdata.DBEvent.get_by_key_name([str(x['eid']) for x in events])
            loaded_fb_event_ids = set(x.fb_event_id for x in db_events if x)

            for event in events:
                # rewrite hack necessary for templates (and above code)
                event['id'] = event['eid']
                event['loaded'] = event['id'] in loaded_fb_event_ids
                for field in ['start_time', 'end_time']:
                    event[field] = dates.localize_timestamp(datetime.datetime.fromtimestamp(event[field]))

            lastadd_key = 'LastAdd.%s' % (self.fb_uid)
            if not smemcache.get(lastadd_key):
                backgrounder.load_events([x['eid'] for x in events])
                smemcache.set(lastadd_key, True, PREFETCH_EVENTS_INTERVAL)

        self.display['events'] = events
        self.display['fb_event'] = fb_event

        self.render_template('add')

    def post(self):
        if self.request.get('event_id'):
            event_id = self.request.get('event_id')
        elif self.request.get('event_url'):
            event_id = get_id_from_url(self.request.get('event_url'))
            if not event_id:
                self.add_error('invalid event_url, expecting eid= parameter')
        else:
            self.add_error('missing event_url or event_id parameter')

        self.batch_lookup.lookup_event(event_id)
        try:
            self.finish_preload()
        except fb_api.FacebookException, e:
            self.add_error(str(e))

        fb_event = self.batch_lookup.data_for_event(event_id)
        if fb_event['info']['privacy'] != 'OPEN':
            self.add_error('Cannot add secret/closed events to dancedeets!')

        self.errors_are_fatal()
        fb_event = self.batch_lookup.data_for_event(event_id)
        e = eventdata.DBEvent.get_or_insert(event_id)
        e.tags = self.request.get_all('tag')
        e.creating_fb_uid = self.user.fb_uid
        e.creation_time = datetime.datetime.now()
        e.make_findable_for(fb_event)
        e.put()

        self.user.add_message('Your event "%s" has been added.' % fb_event['info']['name'])
        self.redirect('/')

class AdminPotentialEventViewHandler(base_servlet.BaseRequestHandler):
    def get(self):
        unseen_potential_events = potential_events.PotentialEvent.gql("WHERE looked_at = :looked_at", looked_at=False)
        potential_event_ids = [x.key().name() for x in unseen_potential_events]
        already_added_events = eventdata.DBEvent.get_by_key_name(potential_event_ids)
        already_added_event_ids = [x.key().name() for x in already_added_events if x]
        # construct a list of not-added ids for display, but keep the list of all ids around so we can still mark them as processed down below
        potential_event_notadded_ids = list(set(potential_event_ids).difference(already_added_event_ids))

        for e in potential_event_notadded_ids:
            self.batch_lookup.lookup_event(e)
        self.finish_preload()

        template_events = []
        for e in potential_event_notadded_ids:
            try:
                fb_event = self.batch_lookup.data_for_event(e)
            except KeyError:
                logging.error("Failed to load event id %s", e)
                continue
            dance_tags = event_classifier.is_dance_event(fb_event)
            if dance_tags:
                dance_words, event_words = dance_tags
                dance_words_str = ', '.join(list(dance_words))
                event_words_str = ', '.join(list(event_words))
            else:
                dance_words_str = 'NONE'
                event_words_str = 'NONE'
            template_events.append(dict(fb_event=fb_event, dance_words=dance_words_str, event_words=event_words_str))
        self.display['potential_events_listing'] = template_events
        self.display['potential_ids'] = ','.join(potential_event_ids) # use all ids, since we want to mark already-added ids as processed as well
        self.render_template('admin_potential_events')

    def post(self):
        processed_ids = self.request.get('processed_ids', '').split(',')
        if processed_ids:
            seen_potential_events = potential_events.PotentialEvent.get_by_key_name(processed_ids)
            for event in seen_potential_events:
                event.looked_at = True
                event.put()
            self.redirect('/events/admin_potential_events')
