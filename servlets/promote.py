import datetime
import logging

import base_servlet
from event_scraper import add_entities
from events import event_locations
from events import eventdata
import fb_api
from nlp import event_auto_classifier
from nlp import event_classifier
from servlets import event as servlets_event
from util import dates

class PromoteHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        if self.user:
            try:
                user_events = self.fbl.get(fb_api.LookupUserEvents, self.fb_uid, allow_cache=False)
                results_json = user_events['all_event_info']['data']
                events = list(reversed(sorted(results_json, key=lambda x: x.get('start_time'))))
            except fb_api.NoFetchedDataException, e:
                logging.error("Could not load event info for user: %s", e)
                events = []

            fb_user = self.fbl.get(fb_api.LookupUser, self.fb_uid)
            print fb_user
            events = [x for x in events if x['host'] == fb_user['profile']['name']]

            #STR_ID_MIGRATE: We still get ids as ints from our FQL
            loaded_fb_event_ids = set(x.string_id() for x in eventdata.DBEvent.get_by_ids([str(x['eid']) for x in events], keys_only=True) if x)

            for event in events:
                # rewrite hack necessary for templates (and above code)
                #STR_ID_MIGRATE
                event['id'] = str(event['eid'])
                event['loaded'] = event['id'] in loaded_fb_event_ids

        self.display['events'] = events
        self.display['parse_fb_timestamp'] = dates.parse_fb_timestamp
        self.render_template('promote')

    def post(self):
        if self.request.get('event_url'):
            event_id = servlets_event.get_id_from_url(self.request.get('event_url'))
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

        privacy = fb_event['info'].get('privacy')
        if privacy != 'OPEN':
            event_errors.append('The event privacy settings are too restricted.')

        classified_event = event_classifier.ClassifiedEvent(fb_event)
        classified_event.classify()
        auto_add_result = event_auto_classifier.is_auto_add_event(classified_event)
        if not auto_add_result[0]:
            event_warnings.append("The event wouldn't be automatically added. There weren't enough strong keywords for the system to identify it.")
        auto_notadd_result = event_auto_classifier.is_auto_notadd_event(classified_event, auto_add_result=auto_add_result)
        if auto_notadd_result[0]:
            event_warnings.append('The event appears to be the "wrong" kind of dance event for DanceDeets. Are you sure it is a street dance event?')

        location_info = event_locations.LocationInfo(fb_event)
        if not location_info.geocode:
            event_errors.append('Your event has no location. Please select a particular address, city, state, or country for this event.')
        elif 'venue' not in fb_event['info']:
            event_warnings.append('For best results, your event should select a location from one of the venues Facebook suggests. DanceDeets believes your event is in %s' % location_info.final_city)

        self.display['event_warnings'] = event_warnings
        self.display['event_errors'] = event_errors
        self.render_template('promote_event')
