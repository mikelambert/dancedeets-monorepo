#!/usr/bin/env python

import json
import logging
import re
import urllib
import urllib2

from google.appengine.ext import deferred

import base_servlet
from events import eventdata
import fb_api
import locations
from logic import add_entities
from logic import backgrounder
from logic import event_auto_classifier
from logic import event_classifier
from logic import event_locations
from logic import event_updates
from logic import potential_events
from logic import rsvp
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

        rsvps = rsvp.RSVPManager(self.fbl)
        success = rsvps.set_rsvp_for_event(self.access_token, event_id, rsvp_status)

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
        return self.redirect(urls.fb_relative_event_url(event_id), permanent=True)

class ShowEventHandler(base_servlet.BaseRequestHandler):

    def requires_login(self):
        return False

    def get(self):
        path_bits = self.request.path.split('/')
        event_id = urllib.unquote(path_bits[2])
        if not event_id:
            self.response.out.write('Need an event_id.')
            return
        if not self.request.path.endswith('/'):
            return self.redirect(urls.fb_relative_event_url(event_id), permanent=True)

        event_info = self.fbl.get(fb_api.LookupEvent, event_id)
        if event_info['empty']:
            self.response.out.write('This event was %s.' % event_info['empty'])
            return

        self.display['new_layout'] = self.request.get('new_layout')
        self.display['cover'] = event_info['info'].get('cover')
        self.display['pic'] = eventdata.get_event_image_url(event_info)

        self.display['start_time'] = dates.parse_fb_start_time(event_info)
        self.display['end_time'] = dates.parse_fb_end_time(event_info)

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
    def show_barebones_page(self, fb_event_id):
        potential_event = potential_events.PotentialEvent.get_by_key_name(fb_event_id)
        e = eventdata.DBEvent.get_by_key_name(fb_event_id)
        if potential_event:
            self.response.out.write('<a href="https://appengine.google.com/datastore/edit?app_id=s~dancedeets-hrd&key=%s">PE</a> ' % potential_event.key().__str__())
        if e:
            self.response.out.write('<a href="https://appengine.google.com/datastore/edit?app_id=s~dancedeets-hrd&key=%s">DBE</a> ' % e.key().__str__())

    def handle_error_response(self, errors):
        event_id = None
        if self.request.get('event_url'):
            event_id = get_id_from_url(self.request.get('event_url'))
        elif self.request.get('event_id'):
            event_id = self.request.get('event_id')
        error_string = ','.join(errors)
        return '%s\n%s' % (error_string, self.show_barebones_page(event_id))

    def get(self):
        event_id = None
        if self.request.get('event_url'):
            event_id = get_id_from_url(self.request.get('event_url'))
        elif self.request.get('event_id'):
            event_id = self.request.get('event_id')
        self.fbl.request(fb_api.LookupEvent, event_id, allow_cache=False)
        self.fbl.request(fb_api.LookupEventAttending, event_id, allow_cache=False)
        self.finish_preload()

        try:
            fb_event = self.fbl.fetched_data(fb_api.LookupEvent, event_id)
            fb_event_attending = self.fbl.fetched_data(fb_api.LookupEventAttending, event_id)
        except fb_api.NoFetchedDataException:
            return self.show_barebones_page(event_id)

        if not fb_api.is_public_ish(fb_event):
            self.add_error('Cannot add secret/closed events to dancedeets!')

        self.errors_are_fatal()

        owner_location = None
        if 'owner' in fb_event['info']:
            owner_id = fb_event['info']['owner']['id']
            try:
                combined_owner = self.fbl.get(fb_api.LookupProfile, owner_id)
            except fb_api.NoFetchedDataException:
                combined_owner = None
            if combined_owner and not combined_owner['empty']:
                owner = combined_owner['profile']
                if 'location' in owner:
                    owner_location = event_locations.city_for_fb_location(owner['location'])
        self.display['owner_location'] = owner_location


        # Don't insert object until we're ready to save it...
        e = eventdata.DBEvent.get_by_key_name(event_id)
        if e and e.creating_fb_uid:
            f = urllib2.urlopen('https://graph.facebook.com/%s?access_token=%s' % (e.creating_fb_uid, self.access_token))
            json_data = json.loads(f.read())
            creating_user = json_data['name']
        else:
            creating_user = None

        potential_event = potential_events.make_potential_event_without_source(event_id, fb_event, fb_event_attending)
        classified_event = event_classifier.get_classified_event(fb_event, potential_event.language)
        self.display['classified_event'] = classified_event
        if classified_event.is_dance_event():
            dance_words_str = ', '.join(list(classified_event.dance_matches()))
            event_words_str = ', '.join(list(classified_event.event_matches()))
        else:
            dance_words_str = 'NONE'
            event_words_str = 'NONE'
        self.display['classifier_dance_words'] = dance_words_str
        self.display['classifier_event_words'] = event_words_str
        self.display['creating_user'] = creating_user

        self.display['potential_event'] = potential_event

        add_result = event_auto_classifier.is_auto_add_event(classified_event)
        notadd_result = event_auto_classifier.is_auto_notadd_event(classified_event, auto_add_result=add_result)
        auto_classified = ''
        if add_result[0]:
            auto_classified += 'add: %s.\n' % add_result[1]
        if notadd_result[0]:
            auto_classified += 'notadd: %s.\n' % notadd_result[1]

        self.display['auto_classified_types'] = auto_classified

        location_info = event_locations.LocationInfo(fb_event, db_event=e, debug=True)
        self.display['location_info'] = location_info
        self.display['fb_geocoded_address'] = locations.get_city_name(address=location_info.fb_address)

        self.display['event'] = e
        self.display['fb_event'] = fb_event

        self.display['highlight_keywords'] = event_classifier.highlight_keywords

        self.display['track_google_analytics'] = False
        self.render_template('admin_edit')

    def post(self):
        event_id = self.request.get('event_id')
        remapped_address = self.request.get('remapped_address')
        override_address = self.request.get('override_address')

        if self.request.get('delete'):
            e = eventdata.DBEvent.get_by_key_name(event_id)
            event_updates.delete_event(e)
            self.user.add_message("Event deleted!")
            return self.redirect('/events/admin_edit?event_id=%s' % event_id)

        if self.request.get('background'):
            deferred.defer(add_entities.add_update_event, event_id, self.user.fb_uid, self.fbl, remapped_address=remapped_address, override_address=override_address, creating_method=eventdata.CM_ADMIN)
            self.response.out.write("<title>Added!</title>Added!")
        else:
            try:
                add_entities.add_update_event(event_id, self.user.fb_uid, self.fbl, remapped_address=remapped_address, override_address=override_address, creating_method=eventdata.CM_ADMIN)
            except Exception, e:
                self.add_error(str(e))
            self.errors_are_fatal()
            self.user.add_message("Changes saved!")
            return self.redirect('/events/admin_edit?event_id=%s' % event_id)

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
            logging.info("Showing page for adding event %s", event_id)
            fb_event = self.fbl.get(fb_api.LookupEvent, event_id)
        else:
            logging.info("Showing page for selecting an event to add")
            try:
                user_events = self.fbl.get(fb_api.LookupUserEvents, self.fb_uid)
                results_json = user_events['all_event_info']['data']
                events = list(reversed(sorted(results_json, key=lambda x: x.get('start_time'))))
            except fb_api.NoFetchedDataException, e:
                logging.error("Could not load event info for user: %s", e)
                events = []
            db_events = eventdata.DBEvent.get_by_key_name([str(x['eid']) for x in events])
            loaded_fb_event_ids = set(x.fb_event_id for x in db_events if x)

            for event in events:
                # rewrite hack necessary for templates (and above code)
                event['id'] = event['eid']
                event['loaded'] = event['id'] in loaded_fb_event_ids

            lastadd_key = 'LastAdd.%s' % (self.fb_uid)
            if not smemcache.get(lastadd_key):
                backgrounder.load_events([x['eid'] for x in events])
                smemcache.set(lastadd_key, True, PREFETCH_EVENTS_INTERVAL)

        self.display['events'] = events
        self.display['fb_event'] = fb_event
        self.display['parse_fb_timestamp'] = dates.parse_fb_timestamp
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

        try:
            fb_event, e = add_entities.add_update_event(event_id, self.user.fb_uid, self.fbl, creating_method=eventdata.CM_USER)
            self.user.add_message('Your event "%s" has been added.' % fb_event['info']['name'])
        except Exception, e:
            self.add_error(str(e))
        self.errors_are_fatal()

        return self.redirect('/')

class AdminNoLocationEventsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        # TODO: There are some events with city_name=Unknown and a valid latitude that are just not near any major metropolis. They are undercounted and have "No Scene", which we may want to fix at some point.
        db_events = eventdata.DBEvent.gql("WHERE city_name = :1 AND latitude = :2 and anywhere != :3", 'Unknown', None, True)
        self.fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in db_events])
        template_events = []
        for e in sorted(db_events, key=lambda x: x.start_time):
            fb_event = self.fbl.fetched_data(fb_api.LookupEvent, e.fb_event_id)
            if not fb_event['empty']:
                template_events.append(dict(fb_event=fb_event, db_event=e))
        self.display['events'] = template_events
        self.render_template('admin_nolocation_events')


class AdminPotentialEventViewHandler(base_servlet.BaseRequestHandler):
    def get(self):
        number_of_events = int(self.request.get('number_of_events', '20'))
        unseen_potential_events = list(potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score > 0 ORDER BY match_score DESC LIMIT %s" % number_of_events))
        if len(unseen_potential_events) < number_of_events:
            unseen_potential_events += list(potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score = 0 AND show_even_if_no_score = True LIMIT %s" % (number_of_events - len(unseen_potential_events))))

        potential_event_dict = dict((x.key().name(), x) for x in unseen_potential_events)
        already_added_events = eventdata.DBEvent.get_by_key_name(list(potential_event_dict))
        already_added_event_ids = [x.key().name() for x in already_added_events if x]
        # construct a list of not-added ids for display, but keep the list of all ids around so we can still mark them as processed down below
        potential_event_notadded_ids = list(set(potential_event_dict).difference(already_added_event_ids))
        potential_event_notadded_ids.sort(key=lambda x: -(potential_event_dict[x].match_score or 0))

        # Limit to 20 at a time so we don't overwhelm the user.
        non_zero_events = potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score > 0").count(20000)
        zero_events = potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score = 0 AND show_even_if_no_score = True").count(20000)
        total_potential_events = non_zero_events + zero_events

        has_more_events = total_potential_events > number_of_events
        potential_event_notadded_ids = potential_event_notadded_ids[:number_of_events]

        self.fbl.request_multi(fb_api.LookupEvent, potential_event_notadded_ids)
        self.fbl.request_multi(fb_api.LookupEventAttending, potential_event_notadded_ids)
        self.finish_preload()

        template_events = []
        for e in potential_event_notadded_ids:
            try:
                fb_event = self.fbl.fetched_data(fb_api.LookupEvent, e)
                fb_event_attending = self.fbl.fetched_data(fb_api.LookupEventAttending, e)
            except KeyError:
                logging.error("Failed to load event id %s", e)
                continue
            if fb_event['empty']:
                continue
            classified_event = event_classifier.get_classified_event(fb_event, potential_event_dict[e])
            if classified_event.is_dance_event():
                reason = classified_event.reason()
                dance_words_str = ', '.join(list(classified_event.dance_matches()))
                event_words_str = ', '.join(list(classified_event.event_matches()))
                wrong_words_str = ', '.join(list(classified_event.wrong_matches()))
            else:
                reason = None
                dance_words_str = 'NONE'
                event_words_str = 'NONE'
                wrong_words_str = 'NONE'
            location_info = event_locations.LocationInfo(fb_event, debug=True)
            potential_event_dict[e] = potential_events.update_scores_for_potential_event(potential_event_dict[e], fb_event, fb_event_attending)
            template_events.append(dict(fb_event=fb_event, classified_event=classified_event, dance_words=dance_words_str, event_words=event_words_str, wrong_words=wrong_words_str, keyword_reason=reason, potential_event=potential_event_dict[e], location_info=location_info))
        self.display['number_of_events']  = number_of_events 
        self.display['total_potential_events'] = '%s + %s' % (non_zero_events, zero_events)
        self.display['has_more_events'] = has_more_events
        self.display['potential_events_listing'] = template_events
        self.display['potential_ids'] = ','.join(already_added_event_ids + potential_event_notadded_ids) # use all ids, since we want to mark already-added ids as processed as well. but only the top N of the potential event ids that we're showing to the user.
        self.display['track_google_analytics'] = False
        self.render_template('admin_potential_events')

    def post(self):
        processed_ids = self.request.get('processed_ids', '').split(',')
        if processed_ids:
            seen_potential_events = potential_events.PotentialEvent.get_by_key_name(processed_ids)
            for event in seen_potential_events:
                event.looked_at = True
                event.put()
            number_of_events = int(self.request.get('number_of_events'))
            return self.redirect('/events/admin_potential_events?number_of_events=%s' % number_of_events)
