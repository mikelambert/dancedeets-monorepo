#!/usr/bin/env python

import datetime
import logging
import re
import time
import urllib2
from django.utils import simplejson

import base_servlet
from events import eventdata
from events import users
from logic import backgrounder
from logic import event_classifier
from logic import event_locations
from logic import potential_events
from logic import rsvp
from logic import thing_db
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

        self.display['pic'] = eventdata.get_event_image_url(self.batch_lookup.data_for_event(event_id)['picture'], eventdata.EVENT_IMAGE_LARGE)

        self.display['start_time'] = dates.parse_fb_timestamp(event_info['info'].get('start_time'))
        self.display['end_time'] = dates.parse_fb_timestamp(event_info['info'].get('end_time'))

        if 'venue' in event_info['info']:
            city_state_country = [
                event_info['info']['venue'][x]
                for x in ['city', 'state', 'country']
                if x in event_info['info']['venue']
            ]
        else:
            city_state_country = ''
        self.display['city_state_country'] = ', '.join(city_state_country)
        self.display['event'] = event_info
        self.display['next'] =  self.request.url
        self.render_template('event_interstitial')

class AdminEditHandler(base_servlet.BaseRequestHandler):
    def get(self):
        event_id = None
        if self.request.get('event_url'):
            event_id = get_id_from_url(self.request.get('event_url'))
        elif self.request.get('event_id'):
            event_id = self.request.get('event_id')
        self.batch_lookup.lookup_event(event_id, allow_cache=False)
        self.finish_preload()

        fb_event = self.batch_lookup.data_for_event(event_id)
        if fb_event['info']['privacy'] != 'OPEN':
            self.add_error('Cannot add secret/closed events to dancedeets!')

        self.errors_are_fatal()

        owner_location = None
        if 'owner' in fb_event['info']:
            owner_id = fb_event['info']['owner']['id']
            new_batch_lookup = self.batch_lookup.copy()
            new_batch_lookup.lookup_profile(owner_id)
            new_batch_lookup.finish_loading()
            owner = new_batch_lookup.data_for_profile(owner_id)['profile']
            if 'location' in owner:
                owner_location = event_locations.city_for_fb_location(owner['location'])
        self.display['owner_location'] = owner_location


        # Don't insert object until we're ready to save it...
        e = eventdata.DBEvent.get_by_key_name(event_id) or eventdata.DBEvent(key_name=event_id)
        if e.creating_fb_uid:
            f = urllib2.urlopen('https://graph.facebook.com/%s?access_token=%s' % (e.creating_fb_uid, self.fb_graph.access_token))
            json = simplejson.loads(f.read())
            creating_user = json['name']
        else:
            creating_user = None

        potential_event = potential_events.PotentialEvent.get_by_key_name(event_id)

        classified_event = event_classifier.get_classified_event(fb_event)
        if classified_event.is_dance_event():
            reason = classified_event.reason()
            dance_words_str = ', '.join(list(classified_event.dance_matches()))
            event_words_str = ', '.join(list(classified_event.event_matches()))
        else:
            reason = None
            dance_words_str = 'NONE'
            event_words_str = 'NONE'
        self.display['classifier_reason'] = reason
        self.display['classifier_dance_words'] = dance_words_str
        self.display['classifier_event_words'] = event_words_str
        self.display['creating_user'] = creating_user

        self.display['potential_event'] = potential_event

        location_info = event_locations.LocationInfo(fb_event, e)
        self.display['location_info'] = location_info
        self.display['fb_geocoded_address'] = locations.get_geocoded_location(location_info.fb_address)['address']

        self.display['event'] = e
        self.display['fb_event'] = fb_event

        self.display['highlight_keywords'] = event_classifier.highlight_keywords

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

        if self.request.get('delete'):
            e = eventdata.DBEvent.get_by_key_name(event_id)
            e.delete()
            self.user.add_message("Event deleted!")
            self.redirect('/events/admin_edit?event_id=%s' % event_id)
            return

        event_locations.update_remapped_address(fb_event, self.request.get('remapped_address'))

        e = eventdata.DBEvent.get_or_insert(event_id)
        e.address = self.request.get('override_address') or None
        e.creating_fb_uid = self.user.fb_uid
        e.creation_time = datetime.datetime.now()
        e.make_findable_for(self.batch_lookup.data_for_event(event_id))
        thing_db.create_source_from_event(e, self.batch_lookup.copy())
        e.put()

        classified_event = event_classifier.get_classified_event(fb_event)
        potential_event = potential_events.PotentialEvent.get_by_key_name(event_id)
        if potential_event:
            for source_id in potential_event.source_ids:
                thing_db.increment_num_real_events(source_id)
                if not classified_event.is_dance_event():
                    thing_db.increment_num_false_negatives(source_id)
        # Hmm, how do we implement this one?# thing_db.increment_num_real_events_without_potential_events(source_id)

        backgrounder.load_event_attending([event_id])
        self.user.add_message("Changes saved!")
        self.redirect('/events/admin_edit?event_id=%s' % event_id)

def get_id_from_url(url):
    if '#' in url:
        url = url.split('#')[1]
    match = re.search('eid=(\d+)', url)
    if not match:
        match = re.search('/events/(\d+)(?:/|$)', url)
        if not match:
            return None
    return match.group(1)

class AddHandler(base_servlet.BaseRequestHandler):
    def get(self):
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
            self.batch_lookup.lookup_user_events(self.fb_uid)
            self.finish_preload()
            try:
                results_json = self.batch_lookup.data_for_user_events(self.fb_uid)['all_event_info']['data']
                events = sorted(results_json, key=lambda x: x.get('start_time'))
            except fb_api.NoFetchedDataException:
                events = []
            db_events = eventdata.DBEvent.get_by_key_name([str(x['eid']) for x in events])
            loaded_fb_event_ids = set(x.fb_event_id for x in db_events if x)

            for event in events:
                # rewrite hack necessary for templates (and above code)
                event['id'] = event['eid']
                event['loaded'] = event['id'] in loaded_fb_event_ids
                for field in ['start_time', 'end_time']:
                    event[field] = dates.localize_timestamp(datetime.datetime.fromtimestamp(event.get(field)))

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
        self.errors_are_fatal()


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
        e.creating_fb_uid = self.user.fb_uid
        e.creation_time = datetime.datetime.now()
        e.make_findable_for(fb_event)
        thing_db.create_source_from_event(e, self.batch_lookup.copy())
        e.put()

        self.user.add_message('Your event "%s" has been added.' % fb_event['info']['name'])
        self.redirect('/')

class AdminNoLocationEventsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        # TODO: There are some events with city_name=Unknown and a valid latitude that are just not near any major metropolis. They are undercounted and have "No Scene", which we may want to fix at some point.
        db_events = eventdata.DBEvent.gql("WHERE city_name = :1 AND latitude = :2 and anywhere != :3", 'Unknown', None, True)
        for e in db_events:
            self.batch_lookup.lookup_event(e.fb_event_id)
        self.finish_preload()
        template_events = []
        for e in db_events:
            fb_event = self.batch_lookup.data_for_event(e.fb_event_id)
            if not fb_event['deleted']:
                template_events.append(dict(fb_event=fb_event, db_event=e))
        self.display['events'] = template_events
        self.render_template('admin_nolocation_events')


class AdminPotentialEventViewHandler(base_servlet.BaseRequestHandler):
    def get(self):
        number_of_events = int(self.request.get('number_of_events', '20'))
        unseen_potential_events = list(potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score > 0"))
        if len(unseen_potential_events) < number_of_events:
            unseen_potential_events += list(potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score = 0 AND show_even_if_no_score = True"))
        potential_event_dict = dict((x.key().name(), x) for x in unseen_potential_events)
        already_added_events = eventdata.DBEvent.get_by_key_name(list(potential_event_dict))
        already_added_event_ids = [x.key().name() for x in already_added_events if x]
        # construct a list of not-added ids for display, but keep the list of all ids around so we can still mark them as processed down below
        potential_event_notadded_ids = list(set(potential_event_dict).difference(already_added_event_ids))
        potential_event_notadded_ids.sort(key=lambda x: -(potential_event_dict[x].match_score or 0))

        # Limit to 20 at a time so we don't overwhelm the user.
        total_potential_events = len(potential_event_notadded_ids)
        has_more_events = total_potential_events > number_of_events
        potential_event_notadded_ids = potential_event_notadded_ids[:number_of_events]

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
            if fb_event['deleted']:
                continue
            classified_event = event_classifier.get_classified_event(fb_event)
            if classified_event.is_dance_event():
                reason = classified_event.reason()
                dance_words_str = ', '.join(list(classified_event.dance_matches()))
                event_words_str = ', '.join(list(classified_event.event_matches()))
            else:
                reason = None
                dance_words_str = 'NONE'
                event_words_str = 'NONE'
            location_info = event_locations.LocationInfo(fb_event)
            template_events.append(dict(fb_event=fb_event, classified_event=classified_event, dance_words=dance_words_str, event_words=event_words_str, keyword_reason=reason, potential_event=potential_event_dict[e], location_info=location_info))
        self.display['number_of_events']  = number_of_events 
        self.display['total_potential_events'] = total_potential_events
        self.display['has_more_events'] = has_more_events
        self.display['potential_events_listing'] = template_events
        self.display['potential_ids'] = ','.join(already_added_event_ids + potential_event_notadded_ids) # use all ids, since we want to mark already-added ids as processed as well. but only the top N of the potential event ids that we're showing to the user.
        self.render_template('admin_potential_events')

    def post(self):
        processed_ids = self.request.get('processed_ids', '').split(',')
        if processed_ids:
            seen_potential_events = potential_events.PotentialEvent.get_by_key_name(processed_ids)
            for event in seen_potential_events:
                event.looked_at = True
                event.put()
            number_of_events = int(self.request.get('number_of_events'))
            self.redirect('/events/admin_potential_events?number_of_events=%s' % number_of_events)
