import datetime
import logging

from dancedeets import app
from dancedeets import base_servlet
from dancedeets import fb_api
from dancedeets.event_scraper import add_entities
from dancedeets.events import event_locations
from dancedeets.events import eventdata
from dancedeets.logic import api_format
from dancedeets.nlp import event_auto_classifier
from dancedeets.nlp import event_classifier
from dancedeets.servlets import event
from dancedeets.util import dates
from dancedeets.util import fb_events
from dancedeets.util import urls


@app.route('/promote')
class PromoteHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get_events(self):
        if not self.user:
            return []

        try:
            user_events = self.fbl.get(fb_api.LookupUserEvents, self.fb_uid, allow_cache=False)
            results_json = user_events['events']['data']
            events = list(reversed(sorted(results_json, key=lambda x: x.get('start_time'))))
        except fb_api.NoFetchedDataException, e:
            logging.error("Could not load event info for user: %s", e)
            events = []

        loaded_fb_event_ids = set(x.string_id() for x in eventdata.DBEvent.get_by_ids([x['id'] for x in events], keys_only=True) if x)

        for e in events:
            e['loaded'] = e['id'] in loaded_fb_event_ids
        return events

    def render_page(self):
        self.jinja_env.filters['parse_fb_timestamp'] = dates.parse_fb_timestamp
        self.display['events'] = self.get_events()
        self.display['event_url'] = self.request.get('event_url')
        self.render_template('promote')

    def get(self):
        self.finish_preload()
        self.render_page()

    def post(self):
        if self.request.get('event_url'):
            event_id = urls.get_event_id_from_url(self.request.get('event_url'))
            if not event_id:
                self.add_error('Unrecognized Facebook event URL')
        else:
            self.add_error('Missing Facebook event URL')
        self.errors_are_fatal()

        event_errors = []
        event_warnings = []
        try:
            fb_event = self.fbl.get(fb_api.LookupEvent, event_id, allow_cache=False)
        except fb_api.NoFetchedDataException:
            event_errors.append('Unable to fetch event. Please adjust your event privacy settings, or log in.')
            return

        if 'cover_info' not in fb_event['info']:
            event_errors.append('The event needs a cover photo.')

        start_time = dates.parse_fb_start_time(fb_event)
        if start_time < datetime.datetime.now() - datetime.timedelta(days=1):
            event_errors.append('Your event appears to be in the past. You should fix the date.')

        if 'name' not in fb_event['info']:
            event_errors.append('The event needs a name.')

        if 'description' not in fb_event['info']:
            event_errors.append('The event needs a description.')

        if not fb_events.is_public(fb_event):
            event_errors.append('The event privacy settings are too restricted.')

        classified_event = event_classifier.classified_event_from_fb_event(fb_event)
        classified_event.classify()
        auto_add_result = event_auto_classifier.is_auto_add_event(classified_event)
        if not auto_add_result[0]:
            event_warnings.append(
                "The event wouldn't be automatically added. There weren't enough strong keywords for the system to identify it."
            )
        auto_notadd_result = event_auto_classifier.is_auto_notadd_event(classified_event, auto_add_result=auto_add_result)
        if auto_notadd_result[0]:
            event_warnings.append(
                'The event appears to be the "wrong" kind of dance event for DanceDeets. Are you sure it is a street dance event?'
            )

        location_info = event_locations.LocationInfo(fb_event)
        if not location_info.geocode:
            event_errors.append('Your event has no location. Please select a particular address, city, state, or country for this event.')
        elif 'place' not in fb_event['info']:
            event_warnings.append(
                'For best results, your event should select a location from one of the venues Facebook suggests. DanceDeets believes your event is in %s'
                % location_info.final_city
            )

        self.display['event_warnings'] = event_warnings
        self.display['event_errors'] = event_errors
        self.display['event'] = fb_event

        # Add Event
        if self.request.get('force_add') or not event_errors:
            self.user.add_message('Your event "%s" has been added.' % fb_event['info']['name'])
            add_entities.add_update_event(fb_event, self.fbl, creating_uid=self.user.fb_uid, creating_method=eventdata.CM_USER)
        self.render_page()


@app.route(r'/promoters/events/(%s)(?:/.*)?' % urls.EVENT_ID_REGEX)
class PromoteEventHandler(base_servlet.BaseRequestHandler):
    def get(self, event_id):
        self.finish_preload()

        # Load the db_event instead of the fb_event, as the db_event is likely to be in cache
        db_event = eventdata.DBEvent.get_by_id(event_id)
        if not db_event:
            self.abort(404)
        if not db_event.has_content():
            self.response.out.write('This event was %s.' % db_event.empty_reason)
            return

        self.display['displayable_event'] = event.DisplayableEvent(db_event)

        # Render React component for inclusion in our template:
        api_event = api_format.canonicalize_event_data(db_event, version=(2, 0))
        props = dict(
            event=api_event,
            forceAdmin=True,
        )
        self.setup_react_template('event.js', props)

        self.render_template('event')
