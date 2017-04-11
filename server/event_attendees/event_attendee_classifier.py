import json
import logging
import time

from google.cloud import datastore

from events import event_locations
import fb_api
from loc import math
from nlp import event_classifier
from rankings import cities
from . import popular_people

def find_overlap(event_attendee_ids, top_dance_attendee_ids):
    if not len(event_attendee_ids):
        return [], None, None
    intersection_ids = set(event_attendee_ids).intersection(top_dance_attendee_ids)
    num_intersection = len(intersection_ids)
    fraction_known = 1.0 * num_intersection / len(event_attendee_ids)
    return intersection_ids, num_intersection, fraction_known

def get_event_attendee_ids(fb_event_attending_maybe):
    if fb_event_attending_maybe['empty']:
        logging.info('Event has no attendees, skipping attendee-based classification.')
        return []

    # Combine both attending AND maybe for looking at people and figuring out if this event is legit
    # Will really help improve the coverage and accuracy versus just using the attendee lists...
    try:
        people = fb_event_attending_maybe['attending']['data'] + fb_event_attending_maybe['maybe']['data']
    except KeyError:
        logging.error('Got corrupted fb_event_attending_maybe: %s', fb_event_attending_maybe)
        return []
    event_attendee_ids = [attendee['id'] for attendee in people]
    if not event_attendee_ids:
        return []
    return event_attendee_ids

def get_bounds_for_fb_event(fb_event, check_places=False):
    # We don't need google-maps latlong accuracy. Let's cheat and use the fb_event for convenience if possible...
    location = fb_event['info'].get('place', {}).get('location', {})
    if location and location.get('latitude') is not None:
        latlong = (location['latitude'], location['longitude'])
        # TODO: Someday we'd like to use locations of Taiwan or Germany to grab a bunch of stuff in those bounds
        # but for now, FB doesn't send us proper lat-long-boxes for them, and I don't want to look up everything
        # just in case there are bigger bounds...so we accept the latlong as-is.
        bounds = math.expand_bounds((latlong, latlong), cities.NEARBY_DISTANCE_KM)
    else:
        logging.info('Looking up event %s LocationInfo', fb_event['info']['id'])
        # Places textsearch lookups turn out to be 10x-expensive against our quota
        # So we disable them here, and instead just rely on the 99% good address searches
        # It should fallback to places on un-geocodable addresses too...
        # But at least it won't try Places *in addition* to geocode lookups.
        location_info = event_locations.LocationInfo(fb_event, check_places=check_places)
        if location_info.geocode:
            bounds = math.expand_bounds(location_info.geocode.latlng_bounds(), cities.NEARBY_DISTANCE_KM)
        else:
            bounds = None
    return bounds

def get_location_style_attendees(fb_event, suspected_dance_event=False, max_attendees=None):
    if suspected_dance_event:
        logging.info('Suspected dance event, so checking place API too just in case.')
    bounds = get_bounds_for_fb_event(fb_event, check_places=suspected_dance_event)
    dance_attendee_styles = popular_people.get_attendees_within(bounds, max_attendees=max_attendees)
    return dance_attendee_styles

def is_good_event_by_attendees(fbl, fb_event, fb_event_attending_maybe=None, classified_event=None):
    matcher = get_matcher(fbl, fb_event, fb_event_attending_maybe, classified_event)
    return matcher.matches[0].overlap_ids if matcher.matches else []

def get_matcher(fbl, fb_event, fb_event_attending_maybe=None, classified_event=None):
    if classified_event is None:
        classified_event = event_classifier.get_classified_event(fb_event)

    event_id = fb_event['info']['id']

    if fb_event_attending_maybe is None:
        try:
            fb_event_attending_maybe = fbl.get(fb_api.LookupEventAttendingMaybe, event_id)
        except fb_api.NoFetchedDataException:
            logging.info('Event %s could not fetch event attendees, aborting.', event_id)
            return False

    matcher = EventAttendeeMatcher(fb_event, fb_event_attending_maybe, classified_event)
    matcher.classify()
    return matcher

class AttendeeMatch(object):
    def __init__(self, name, top_n, overlap_ids, reason):
        # TODO: clean up our city passing
        category, city = name.split(': ', 1)
        self.name = name
        self.category = category
        self.city_name = city
        self.top_n = top_n
        self.overlap_ids = overlap_ids
        self.reason = reason

    def __repr__(self):
        return '%s(**%r)' % (self.__class__.__name__, self.__dict__)

    def get_attendee_lookups(self):
        client = datastore.Client()

        debug_keys = []
        for person_id in self.overlap_ids:
            debug_key = popular_people.PRDebugAttendee.generate_key(self.city_name, self.category, person_id)
            debug_keys.append(client.key('PRDebugAttendee', debug_key))

        missing_keys = []
        print debug_keys
        debug_attendees = client.get_multi(debug_keys, missing_keys)
        print debug_attendees
        person_to_hash_and_event_ids = dict((x['person_id'], json.loads(x['grouped_event_ids'])) for x in debug_attendees)
        return person_to_hash_and_event_ids

class EventAttendeeMatcher(object):
    def __init__(self, fb_event, fb_event_attending_maybe, classified_event):
        self.fb_event = fb_event
        self.fb_event_attending_maybe = fb_event_attending_maybe
        self.classified_event = classified_event

        self.dance_style_attendees = []

        self.matches = []
        self.results = []

        self.overlap_ids = set()

    def classify(self):
        event_id = self.fb_event['info']['id']
        self.event_attendee_ids = get_event_attendee_ids(self.fb_event_attending_maybe)
        if self.event_attendee_ids:
            # If it's a suspected dance event, then we'll fall-through and check the places API for the location data
            # This ensures that any suspected dance events will get proper dance-attendees, and be more likely to be found.
            suspected_dance_event = self.classified_event.dance_event or len(self.classified_event.found_dance_matches) >= 2
            start_time = time.time()
            self.dance_style_attendees = get_location_style_attendees(self.fb_event, suspected_dance_event=suspected_dance_event, max_attendees=100)
            logging.info('Lookup for dancers in event location took %0.3f.', time.time() - start_time)

            # Raise the threshold for regular un-dance-y events, for what it means to 'be a dance event'
            if suspected_dance_event:
                mult = 1.0
            # This will affect various club events too...
            else:
                mult = 2.0

            for name, dance_attendees in self.dance_style_attendees.iteritems():
                # logging.info('%s Attendees Nearby:\n%s', style_name, '\n'.join(repr(x) for x in dance_attendees))
                dance_attendee_ids = [x['id'] for x in dance_attendees]

                overlap_ids, count, fraction = find_overlap(self.event_attendee_ids, dance_attendee_ids[:20])
                self.overlap_ids.update(overlap_ids)
                reason = 'Event %s has %s ids, intersection is %s ids (%.1f%%)' % (event_id, len(self.event_attendee_ids), count, 100.0 * fraction)
                logging.info('%s Attendee-Detection-Top-20: %s', name, reason)
                if count > 0:
                    self.results += ['%s Top20: %s (%.1f%%)' % (name, count, 100.0 * fraction)]
                if (
                    (fraction >= 0.05 * mult and count >= 3) or
                    (fraction >= 0.006 * mult and count >= 4) or # catches 4-or-more on events 666-or-less
                    False
                ):
                    logging.info('Attendee-Detection-Top-20: Attendee-based classifier match: %s', reason)
                    self.results[-1] += ' GOOD!'
                    self.matches.append(AttendeeMatch(name, 20, overlap_ids, reason))

                overlap_ids, count, fraction = find_overlap(self.event_attendee_ids, dance_attendee_ids[:100])
                self.overlap_ids.update(overlap_ids)
                reason = 'Event %s has %s ids, intersection is %s ids (%.1f%%)' % (event_id, len(self.event_attendee_ids), count, 100.0 * fraction)
                logging.info('%s Attendee-Detection-Top-100: %s', name, reason)
                if count > 0:
                    self.results += ['%s Top100: %s (%.1f%%)' % (name, count, 100.0 * fraction)]
                if (
                    (fraction >= 0.10 * mult and count >= 3) or
                    (fraction >= 0.05 * mult and count >= 4) or
                    (fraction >= 0.006 * mult and count >= 6) or # catches 6-or-more on events 1K-or-less
                    # Is this a good idea? Would help with 370973376344784
                    # (fraction >= 0.002 * mult and count >= 12) or
                    False
                ):
                    logging.info('%s Attendee-Detection-Top-100: Attendee-based classifier match: %s', name, reason)
                    self.results[-1] += ' GOOD!'
                    self.matches.append(AttendeeMatch(name, 100, overlap_ids, reason))

                # TODO: Disable for now...
                # Basically, cities that have a few events that mix streetdance-and-nonstreetdance
                # will get a bunch of people that are "other-styled dancers"
                # and that, in turn, will cause these to trigger on "any old dance event"
                # Perhaps should find a way to better target our audience as "only counting for events that are purely street dance" ?
                # Or some weighted computation?
                if False:
                    overlap_ids, count, fraction = find_overlap(self.event_attendee_ids, dance_attendee_ids[:500])
                    reason = 'Event %s has %s ids, intersection is %s ids (%.1f%%)' % (event_id, len(self.event_attendee_ids), count, 100.0 * fraction)
                    logging.info('%s Attendee-Detection-Top-500: %s', name, reason)
                    if count > 0:
                        self.results += ['%s Top500: %s (%.1f%%)' % (name, count, 100.0 * fraction)]
                    if (
                        (fraction >= 0.20 * mult and count >= 5) or
                        (fraction >= 0.01 * mult and count >= 15) or
                        (fraction >= 0.001 * mult and count >= 50) or
                        False
                    ):
                        logging.info('%s Attendee-Detection-Top-500: Attendee-based classifier match: %s', name, reason)
                        self.results[-1] += ' GOOD!'
                        self.matches.append(AttendeeMatch(name, 500, overlap_ids, reason))
