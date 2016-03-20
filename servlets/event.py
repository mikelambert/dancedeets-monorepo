#!/usr/bin/env python

import jinja2
import logging
import os
import re
import urllib

from google.appengine.ext import deferred

import app
import base_servlet
from event_scraper import add_entities
from event_scraper import potential_events
from events import eventdata
from events import event_locations
from events import event_reloading_tasks
from events import event_updates
import fb_api
from loc import formatting
from loc import gmaps_api
from logic import rsvp
from nlp import categories
from nlp import event_auto_classifier
from nlp import event_classifier
from search import search_base
from util import dates
from util import urls

PREFETCH_EVENTS_INTERVAL = 24 * 60 * 60


@app.route('/events/rsvp_ajax')
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


@app.route('/events/redirect')
class RedirectToEventHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        event_id = self.request.get('event_id')
        if not event_id:
            self.response.out.write('Need an event_id.')
            return
        return self.redirect(urls.fb_relative_event_url(event_id), permanent=True)


@app.route(r'/events/\d+/?')
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

        # Load the db_event instead of the fb_event, as the db_event is likely to be in cache
        db_event = eventdata.DBEvent.get_by_id(event_id)
        if not db_event:
            self.abort(404)
        if not db_event.has_content():
            self.response.out.write('This event was %s.' % db_event.empty_reason)
            return

        self.display['displayable_event'] = DisplayableEvent(db_event)

        self.display['next'] = self.request.url
        self.display['show_mobile_app_promo'] = True
        self.jinja_env.filters['make_category_link'] = lambda lst: [jinja2.Markup('<a href="/?keywords=%s">%s</a>') % (x, x) for x in lst]

        self.display['canonical_url'] = 'http://%s/events/%s/' % (self._get_full_hostname(), db_event.fb_event_id)

        if self.request.get('amp'):
            if self.display['displayable_event'].largest_cover:
                # Because minification interferes with html-validity when producing:
                # <meta name=viewport content=width=device-width,minimum-scale=1,initial-scale=1,maximum-scale=1,user-scalable=no>
                self.allow_minify = False
                event_amp_css_filename = os.path.join(os.path.dirname(__file__), '..', 'dist-includes/css/event-amp.css')
                event_amp_css = open(event_amp_css_filename).read()
                event_amp_css = re.sub(r'@-ms-viewport\s*{.*?}', '', event_amp_css)
                event_amp_css = re.sub(r'!important', '', event_amp_css)
                event_amp_css = event_amp_css.replace('url(..', 'url(/dist-' + self._get_static_version())
                self.display['event_amp_stylesheet'] = event_amp_css
                self.render_template('event_amp')
            else:
                self.abort(404)
        else:
            self.render_template('event')


def join_valid(sep, lst):
    return sep.join(x for x in lst if x)


class DisplayableEvent(object):
    """Encapsulates all the data (and relevant accessor methods) for showing an event on the event page."""

    def __init__(self, db_event):
        self.db_event = db_event

    def location_schema_html(self):
        html = [
            '<span itemscope itemprop="location" itemtype="http://schema.org/Place">',
            '  <meta itemprop="name" content="%s" />' % self.db_event.location_name,
        ]
        if self.latitude:
            html += [
                '  <span itemprop="geo" itemscope itemtype="http://schema.org/GeoCoordinates">',
                '    <meta itemprop="latitude" content="%s" />' % self.db_event.latitude,
                '    <meta itemprop="longitude" content="%s" />' % self.db_event.longitude,
                '  </span>',
            ]
        if self.venue:
            html += [
                '  <span itemprop="address" itemscope itemtype="http://schema.org/PostalAddress">',
            ]
            if self.street_address:
                html += ['    <meta itemprop="streetAddress" content="%s"/>' % self.db_event.street_address]
            if self.city:
                html += ['    <meta itemprop="addressLocality" content="%s"/>' % self.db_event.city]
            if self.street_address:
                html += ['    <meta itemprop="addressRegion" content="%s"/>' % self.db_event.state]
            if self.street_address:
                html += ['    <meta itemprop="addressCountry" content="%s"/>' % self.db_event.country]
            html += ['  </span>']
        html += [
            '</span>',
        ]
        return jinja2.Markup('\n'.join(html))

    @property
    def meta_description(self):
        formatted_start_time = self.db_event.start_time.strftime('%Y/%m/%d @ %H:%M')

        formatted_location = join_valid(', ', [
            self.db_event.location_name,
            self.db_event.city,
            self.db_event.state,
        ])
        return join_valid(': ', [
            formatted_start_time,
            formatted_location,
            self.db_event.description,
        ])

    def __getattr__(self, name):
        return getattr(self.db_event, name)


@app.route('/events/admin_edit')
class AdminEditHandler(base_servlet.BaseRequestHandler):
    def show_barebones_page(self, fb_event_id):
        potential_event = potential_events.PotentialEvent.get_by_key_name(fb_event_id)
        e = eventdata.DBEvent.get_by_id(fb_event_id)
        if potential_event:
            self.response.out.write('<a href="https://appengine.google.com/datastore/edit?app_id=s~dancedeets-hrd&key=%s">PE</a> ' % potential_event.key().__str__())
        if e:
            self.response.out.write('<a href="https://appengine.google.com/datastore/edit?app_id=s~dancedeets-hrd&key=%s">DBE</a> ' % e.key.urlsafe())

    def handle_error_response(self, errors):
        event_id = None
        if self.request.get('event_url'):
            event_id = get_id_from_url(self.request.get('event_url'))
        elif self.request.get('event_id'):
            event_id = self.request.get('event_id')
        error_string = ','.join(errors)
        return '%s\n%s' % (error_string, self.show_barebones_page(event_id))

    def _get_location(self, fb_id, fb_type, key):
        try:
            obj = self.fbl.get(fb_type, fb_id)
        except fb_api.NoFetchedDataException:
            pass
        else:
            if obj and not obj['empty']:
                return obj[key].get('location')
        return None

    def get(self):
        event_id = None
        if self.request.get('event_url'):
            event_id = get_id_from_url(self.request.get('event_url'))
        elif self.request.get('event_id'):
            event_id = self.request.get('event_id')
        self.fbl.request(fb_api.LookupEvent, event_id, allow_cache=False)
        # DISABLE_ATTENDING
        # self.fbl.request(fb_api.LookupEventAttending, event_id, allow_cache=False)
        self.finish_preload()

        try:
            fb_event = self.fbl.fetched_data(fb_api.LookupEvent, event_id)
            # DISABLE_ATTENDING
            fb_event_attending = None
            # fb_event_attending = fbl.fetched_data(fb_api.LookupEventAttending, event_id)
        except fb_api.NoFetchedDataException:
            return self.show_barebones_page(event_id)

        if not fb_api.is_public_ish(fb_event):
            self.add_error('Cannot add secret/closed events to dancedeets!')

        self.errors_are_fatal()

        owner_location = None
        if 'owner' in fb_event['info']:
            owner_id = fb_event['info']['owner']['id']
            location = self._get_location(owner_id, fb_api.LookupProfile, 'profile') or self._get_location(owner_id, fb_api.LookupThingFeed, 'info')
            if location:
                owner_location = event_locations.city_for_fb_location(location)
        self.display['owner_location'] = owner_location

        # Don't insert object until we're ready to save it...
        e = eventdata.DBEvent.get_by_id(event_id)
        if e and e.creating_fb_uid:
            creating_user = self.fbl.get(fb_api.LookupUser, e.creating_fb_uid)
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
        styles = categories.find_styles(fb_event) + categories.find_event_types(fb_event)
        self.display['auto_categorized_types'] = ', '.join(x.public_name for x in styles)

        location_info = event_locations.LocationInfo(fb_event, db_event=e, debug=True)
        self.display['location_info'] = location_info
        fb_geocode = gmaps_api.get_geocode(address=location_info.fb_address)
        self.display['fb_geocoded_address'] = formatting.format_geocode(fb_geocode)

        self.display['event'] = e
        self.display['fb_event'] = fb_event

        self.jinja_env.filters['highlight_keywords'] = event_classifier.highlight_keywords

        self.display['track_analytics'] = False
        self.render_template('admin_edit')

    def post(self):
        event_id = self.request.get('event_id')
        remapped_address = self.request.get('remapped_address')
        override_address = self.request.get('override_address')

        if self.request.get('delete'):
            e = eventdata.DBEvent.get_by_id(event_id)
            # This e will be None if the user submits a deletion-form twice
            if e:
                event_updates.delete_event(e)
            self.user.add_message("Event deleted!")
            return self.redirect('/events/admin_edit?event_id=%s' % event_id)

        # We could be looking at a potential event for something that is inaccessable to our admin.
        # So we want to grab the cached value here if possible, which should exist given the admin-edit flow.
        fb_event = self.fbl.get(fb_api.LookupEvent, event_id)
        if self.request.get('background'):
            deferred.defer(add_entities.add_update_event, fb_event, self.fbl, creating_uid=self.user.fb_uid, remapped_address=remapped_address, override_address=override_address, creating_method=eventdata.CM_ADMIN)
            self.response.out.write("<title>Added!</title>Added!")
        else:
            try:
                add_entities.add_update_event(fb_event, self.fbl, creating_uid=self.user.fb_uid, remapped_address=remapped_address, override_address=override_address, creating_method=eventdata.CM_ADMIN)
            except Exception as e:
                self.add_error(str(e))
            self.errors_are_fatal()
            self.user.add_message("Changes saved!")
            return self.redirect('/events/admin_edit?event_id=%s' % event_id)


def get_id_from_url(url):
    if '#' in url:
        url = url.split('#')[1]
    match = re.search(r'eid=(\d+)', url)
    if not match:
        match = re.search(r'/events/(\d+)(?:/|$)', url)
        if not match:
            return None
    return match.group(1)


@app.route('/events_add')
class AddHandler(base_servlet.BaseRequestHandler):
    def get(self):
        fb_event = None
        events = []

        if self.request.get('event_url'):
            event_id = get_id_from_url(self.request.get('event_url'))
        else:
            event_id = self.request.get('event_id')
        if event_id and not self._errors:
            logging.info("Showing page for adding event %s", event_id)
            fb_event = self.fbl.get(fb_api.LookupEvent, event_id)
        else:
            logging.info("Showing page for selecting an event to add. Querying user %s", self.fb_uid)
            try:
                user_events = self.fbl.get(fb_api.LookupUserEvents, self.fb_uid, allow_cache=False)
            except fb_api.NoFetchedDataException as e:
                try:
                    user_events = self.fbl.get(fb_api.LookupUserEvents, self.fb_uid)
                except fb_api.NoFetchedDataException, e:
                    logging.error("Could not load event info for user: %s", e)
                    user_events = None
            if user_events is not None:
                results_json = fb_api.LookupUserEvents.all_events(user_events)
                events = list(sorted(results_json, key=lambda x: x.get('start_time')))
            else:
                events = []
            loaded_fb_events = eventdata.DBEvent.get_by_ids([x['id'] for x in events])
            loaded_fb_event_lookup = dict((x.key.string_id(), x) for x in loaded_fb_events if x)

            for event in events:
                event['loaded'] = event['id'] in loaded_fb_event_lookup

            if self.request.get('new_only') == '1':
                events = [x for x in events if not x['loaded']]

            # HACK: if we detected different data between the FB pseudo-event data and our local events, trigger a refresh
            # This can happen if a user takes an 'old' event that has become PAST, and puts the event in the future,
            # bypassing our optimization attempts to only refresh FUTURE/ONGOING events. This is a fail-safe for that.
            reload_events = []
            for event in events:
                loaded_event = loaded_fb_event_lookup.get(event['id'])
                if loaded_event:
                    if loaded_event.start_time != dates.parse_fb_timestamp(event['start_time']):
                        reload_events.append(loaded_event)
            if reload_events:
                self.fbl.allow_cache = False
                logging.info("Dates changed, reloading events: %s", [x.key.string_id() for x in reload_events])
                event_reloading_tasks.load_fb_event(self.fbl, reload_events)

        self.display['events'] = events
        self.display['fb_event'] = fb_event
        self.jinja_env.filters['parse_fb_timestamp'] = dates.parse_fb_timestamp
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

        try:
            # Skip cache so we always get latest data for newly-added event
            fb_event = self.fbl.get(fb_api.LookupEvent, event_id, allow_cache=False)
            add_entities.add_update_event(fb_event, self.fbl, creating_uid=self.user.fb_uid, creating_method=eventdata.CM_USER)
        except Exception as e:
            self.add_error(str(e))

        self.errors_are_fatal()

        if self.request.get('ajax'):
            self.write_json_response({'success': True})
            return
        else:
            self.user.add_message('Your event "%s" has been added.' % fb_event['info']['name'])

        return self.redirect('/')


@app.route('/events/admin_nolocation_events')
class AdminNoLocationEventsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        num_events = int(self.request.get('num_events', 100))
        # TODO: There are some events with city_name=Unknown and a valid latitude that are just not near any major metropolis. They are undercounted and have "No Scene", which we may want to fix at some point.
        db_events = eventdata.DBEvent.query(eventdata.DBEvent.city_name == 'Unknown').order(-eventdata.DBEvent.start_time).fetch(num_events)
        db_events = [x for x in db_events if x.anywhere is False]
        template_events = []
        for db_event in db_events:
            if db_event.has_content():
                template_events.append(dict(fb_event=db_event.fb_event, db_event=db_event))
        self.display['events'] = template_events
        self.render_template('admin_nolocation_events')


@app.route('/events/admin_potential_events')
class AdminPotentialEventViewHandler(base_servlet.BaseRequestHandler):
    def get(self):

        past_event = self.request.get('past_event', None)
        if past_event == '1':
            past_event = True
        elif past_event == '0':
            past_event = False
        if past_event is not None:
            past_event_query = 'AND past_event = %s' % past_event
        else:
            past_event_query = ''

        number_of_events = int(self.request.get('number_of_events', '20'))
        unseen_potential_events = list(potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score > 0 %s ORDER BY match_score DESC LIMIT %s" % (past_event_query, number_of_events)))
        if len(unseen_potential_events) < number_of_events:
            unseen_potential_events += list(potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score = 0 AND show_even_if_no_score = True %s ORDER BY match_score DESC LIMIT %s" % (past_event_query, number_of_events - len(unseen_potential_events))))

        potential_event_dict = dict((x.key().name(), x) for x in unseen_potential_events)
        already_added_event_ids = [x.string_id() for x in eventdata.DBEvent.get_by_ids(list(potential_event_dict), keys_only=True) if x]
        # construct a list of not-added ids for display, but keep the list of all ids around so we can still mark them as processed down below
        potential_event_notadded_ids = list(set(potential_event_dict).difference(already_added_event_ids))
        potential_event_notadded_ids.sort(key=lambda x: -(potential_event_dict[x].match_score or 0))

        # Limit to 20 at a time so we don't overwhelm the user.
        non_zero_events = potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score > 0 %s" % past_event_query).count(20000)
        zero_events = potential_events.PotentialEvent.gql("WHERE looked_at = NULL AND match_score = 0 AND show_even_if_no_score = True %s" % past_event_query).count(20000)
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
        self.display['number_of_events'] = number_of_events
        self.display['total_potential_events'] = '%s + %s' % (non_zero_events, zero_events)
        self.display['has_more_events'] = has_more_events
        self.display['potential_events_listing'] = template_events
        self.display['potential_ids'] = ','.join(already_added_event_ids + potential_event_notadded_ids)  # use all ids, since we want to mark already-added ids as processed as well. but only the top N of the potential event ids that we're showing to the user.
        self.display['track_analytics'] = False
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
