import datetime
import logging
import re

import fb_api

from events import eventdata
from events import event_locations
from logic import popular_people
import event_types
from loc import math
from nlp import event_auto_classifier
from nlp import event_classifier
from rankings import cities
from util import fb_mapreduce
from util import mr
from . import add_entities
from . import potential_events


def is_good_event_by_text(fb_event, classified_event):
    return event_auto_classifier.is_auto_add_event(classified_event)[0]

def find_overlap(event_attendee_ids, top_dance_attendee_ids):
    if not len(event_attendee_ids):
        return [], None, None
    intersection_ids = set(event_attendee_ids).intersection(top_dance_attendee_ids)
    num_intersection = len(intersection_ids)
    fraction_known = 1.0 * num_intersection / len(event_attendee_ids)
    return intersection_ids, num_intersection, fraction_known

def get_event_attendee_ids(fbl, fb_event, fb_event_attending_maybe=None):
    event_id = fb_event['info']['id']

    if fb_event_attending_maybe is None:
        try:
            fb_event_attending_maybe = fbl.get(fb_api.LookupEventAttendingMaybe, event_id)
        except fb_api.NoFetchedDataException:
            logging.info('Event %s could not fetch event attendees, aborting.', event_id)
            return []
    if fb_event_attending_maybe['empty']:
        logging.info('Event %s has no attendees, skipping attendee-based classification.', event_id)
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
        bounds = math.expand_bounds((latlong, latlong), cities.NEARBY_DISTANCE_KM)
    else:
        logging.info('Looking up event %s LocationInfo', fb_event['info']['id'])
        # Places textsearch lookups turn out to be 10x-expensive against our quota
        # So we disable them here, and instead just rely on the 99% good address searches
        # It should fallback to places on un-geocodable addresses too...
        # But at least it won't try Places *in addition* to geocode lookups.
        location_info = event_locations.LocationInfo(fb_event, check_places=check_places)
        bounds = location_info.geocode.latlng_bounds()
    return bounds

def get_location_style_attendees(fb_event, suspected_dance_event=False):
    if suspected_dance_event:
        logging.info('Suspected dance event, so checking place API too just in case.')
    bounds = get_bounds_for_fb_event(fb_event, check_places=suspected_dance_event)
    dance_attendee_styles = popular_people.get_attendees_within(bounds)
    return dance_attendee_styles

def is_good_event_by_attendees(fbl, fb_event, fb_event_attending_maybe=None, classified_event=None, debug=False):
    event_id = fb_event['info']['id']

    good_event = []
    results = []

    if classified_event is None:
        classified_event = event_classifier.get_classified_event(fb_event)
    event_attendee_ids = get_event_attendee_ids(fbl, fb_event, fb_event_attending_maybe)
    if event_attendee_ids:
        # If it's a suspected dance event, then we'll fall-through and check the places API for the location data
        # This ensures that any suspected dance events will get proper dance-attendees, and be more likely to be found.
        suspected_dance_event = classified_event.dance_event or len(classified_event.found_dance_matches) >= 2
        dance_style_attendees = get_location_style_attendees(fb_event, suspected_dance_event=suspected_dance_event)
        logging.info('Computing Styles for Event')
        # Don't care about which style this event is in...we may misclassify it due to poor keywords
        # So instead let's check *all* the styles
        styles = event_types.STYLES

        # Raise the threshold for regular un-dance-y events, for what it means to 'be a dance event'
        if suspected_dance_event:
            mult = 1.0
        # This will affect various club events too...
        else:
            mult = 2.0

        for style in [None] + sorted(styles):
            style_name = style.public_name if style else ''
            dance_attendees = dance_style_attendees.get(style_name, [])
            # logging.info('%s Attendees Nearby:\n%s', style_name, '\n'.join(repr(x) for x in dance_attendees))
            dance_attendee_ids = [x['id'] for x in dance_attendees]

            overlap_ids, count, fraction = find_overlap(event_attendee_ids, dance_attendee_ids[:20])
            reason = 'Event %s has %s ids, intersection is %s ids (%.1f%%)' % (event_id, len(event_attendee_ids), count, 100.0 * fraction)
            logging.info('%s Attendee-Detection-Top-20: %s', style_name, reason)
            if count > 0:
                results += ['%s Top20: %s (%.1f%%)' % (style_name, count, 100.0 * fraction)]
            if (
                (fraction >= 0.05 * mult and count >= 3) or
                (fraction >= 0.006 * mult and count >= 4) or # catches 4-or-more on events 666-or-less
                False
            ):
                logging.info('Attendee-Detection-Top-20: Attendee-based classifier match: %s', reason)
                results[-1] += ' GOOD!'
                good_event = overlap_ids

            overlap_ids, count, fraction = find_overlap(event_attendee_ids, dance_attendee_ids[:100])
            reason = 'Event %s has %s ids, intersection is %s ids (%.1f%%)' % (event_id, len(event_attendee_ids), count, 100.0 * fraction)
            logging.info('%s Attendee-Detection-Top-100: %s', style_name, reason)
            if count > 0:
                results += ['%s Top100: %s (%.1f%%)' % (style_name, count, 100.0 * fraction)]
            if (
                (fraction >= 0.10 * mult and count >= 3) or
                (fraction >= 0.05 * mult and count >= 4) or
                (fraction >= 0.006 * mult and count >= 6) or # catches 6-or-more on events 1K-or-less
                # Is this a good idea? Would help with 370973376344784
                # (fraction >= 0.002 * mult and count >= 12) or
                False
            ):
                logging.info('%s Attendee-Detection-Top-100: Attendee-based classifier match: %s', style_name, reason)
                results[-1] += ' GOOD!'
                good_event = overlap_ids

            # TODO: Disable for now...
            # Basically, cities that have a few events that mix streetdance-and-nonstreetdance
            # will get a bunch of people that are "other-styled dancers"
            # and that, in turn, will cause these to trigger on "any old dance event"
            # Perhaps should find a way to better target our audience as "only counting for events that are purely street dance" ?
            # Or some weighted computation?
            if False:
                overlap_ids, count, fraction = find_overlap(event_attendee_ids, dance_attendee_ids[:500])
                reason = 'Event %s has %s ids, intersection is %s ids (%.1f%%)' % (event_id, len(event_attendee_ids), count, 100.0 * fraction)
                logging.info('%s Attendee-Detection-Top-500: %s', style_name, reason)
                if count > 0:
                    results += ['%s Top500: %s (%.1f%%)' % (style_name, count, 100.0 * fraction)]
                if (
                    (fraction >= 0.20 * mult and count >= 5) or
                    (fraction >= 0.01 * mult and count >= 15) or
                    (fraction >= 0.001 * mult and count >= 50) or
                    False
                ):
                    logging.info('%s Attendee-Detection-Top-500: Attendee-based classifier match: %s', style_name, reason)
                    results[-1] += ' GOOD!'
                    good_event = overlap_ids

    if debug:
        return good_event, results
    else:
        return good_event

def classify_events(fbl, pe_list, fb_list):
    new_pe_list = []
    new_fb_list = []
    # Go through and find all potential events we actually want to attempt to classify
    for pe, fb_event in zip(pe_list, fb_list):
        # Get these past events out of the way, saved, then continue.
        # Next time through this mapreduce, we shouldn't need to process them.
        if pe.set_past_event(fb_event):
            pe.put()

        if not fb_event or fb_event['empty']:
            continue

        # Don't process events we've already looked at, or don't need to look at.
        # This doesn't happen with the mapreduce that pre-filters them out,
        # but it does happen when we scrape users potential events and throw them all in here.
        if pe.looked_at:
            logging.info('Already looked at event (added, or manually discarded), so no need to re-process.')
            continue

        event_id = pe.fb_event_id
        if not re.match(r'^\d+$', event_id):
            logging.error('Found a very strange potential event id: %s', event_id)
            continue

        new_pe_list.append(pe)
        new_fb_list.append(fb_event)

    logging.info('Filtering out already-added events and others, have %s remaining events to run the classifier on', len(new_pe_list))
    fb_event_ids = [x.fb_event_id for x in new_pe_list]
    fb_attending_maybe_list = fbl.get_multi(fb_api.LookupEventAttendingMaybe, fb_event_ids, allow_fail=True)

    results = []
    for pe, fb_event, fb_event_attending_maybe in zip(new_pe_list, new_fb_list, fb_attending_maybe_list):
        event_id = pe.fb_event_id
        logging.info('Is Good Event By Text: %s: Checking...', event_id)
        classified_event = event_classifier.get_classified_event(fb_event)
        auto_add_result = event_auto_classifier.is_auto_add_event(classified_event)
        logging.info('Is Good Event By Text: %s: %s', event_id, auto_add_result)
        good_event = False
        if auto_add_result and auto_add_result[0]:
            good_event = auto_add_result[0]
            method = eventdata.CM_AUTO
        elif fb_event_attending_maybe:
            logging.info('Is Good Event By Attendees: %s: Checking...', event_id)
            good_event = is_good_event_by_attendees(
                fbl,
                fb_event,
                fb_event_attending_maybe=fb_event_attending_maybe,
                classified_event=classified_event
            )
            logging.info('Is Good Event By Attendees: %s: %s', event_id, good_event)
            method = eventdata.CM_AUTO_ATTENDEE
        if good_event:
            result = '+%s\n' % '\t'.join((pe.fb_event_id, fb_event['info'].get('name', '')))
            try:
                logging.info('VTFI %s: Adding event %s, due to pe-invite-ids: %s', event_id, event_id, pe.get_invite_uids())
                e = add_entities.add_update_event(fb_event, fbl, visible_to_fb_uids=pe.get_invite_uids(), creating_method=method)
                pe2 = potential_events.PotentialEvent.get_by_key_name(pe.fb_event_id)
                pe2.looked_at = True
                pe2.auto_looked_at = True
                pe2.put()
                # TODO(lambert): handle un-add-able events differently
                results.append(result)
                mr.increment('auto-added-dance-events')
                if e.start_time < datetime.datetime.now():
                    mr.increment('auto-added-dance-events-past')
                else:
                    mr.increment('auto-added-dance-events-future')
            except fb_api.NoFetchedDataException as e:
                logging.error("Error adding event %s, no fetched data: %s", pe.fb_event_id, e)
            except add_entities.AddEventException as e:
                logging.warning("Error adding event %s, no fetched data: %s", pe.fb_event_id, e)
        auto_notadd_result = event_auto_classifier.is_auto_notadd_event(classified_event, auto_add_result=auto_add_result)
        if auto_notadd_result[0]:
            pe2 = potential_events.PotentialEvent.get_by_key_name(pe.fb_event_id)
            pe2.looked_at = True
            pe2.auto_looked_at = True
            pe2.put()
            result = '-%s\n' % '\t'.join(unicode(x) for x in (pe.fb_event_id, fb_event['info'].get('name', '')))
            results.append(result)
            mr.increment('auto-notadded-dance-events')
    return results


def classify_events_with_yield(fbl, pe_list):
    fb_list = fbl.get_multi(fb_api.LookupEvent, [x.fb_event_id for x in pe_list], allow_fail=True)
    results = classify_events(fbl, pe_list, fb_list)
    yield ''.join(results).encode('utf-8')

map_classify_events = fb_mapreduce.mr_wrap(classify_events_with_yield)


def mr_classify_potential_events(fbl, past_event, dancey_only):
    filters = [('looked_at', '=', None)]
    if dancey_only:
        filters.append(('should_look_at', '=', True))
    if past_event is not None:
        filters.append(('past_event', '=', past_event))
    fb_mapreduce.start_map(
        fbl,
        'Auto-Add Events',
        'event_scraper.auto_add.map_classify_events',
        'event_scraper.potential_events.PotentialEvent',
        filters=filters,
        handle_batch_size=20,
        queue='fast-queue',
        output_writer_spec='mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        output_writer={
            'mime_type': 'text/plain',
            'bucket_name': 'dancedeets-hrd.appspot.com',
        },
    )
