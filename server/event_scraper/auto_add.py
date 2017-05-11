import datetime
import logging
import re

import fb_api

from event_attendees import event_attendee_classifier
from events import eventdata
from nlp import event_auto_classifier
from nlp import event_classifier
from util import fb_mapreduce
from util import mr
from . import add_entities
from . import potential_events

def is_good_event_by_text(fb_event, classified_event):
    return event_auto_classifier.is_auto_add_event(classified_event)[0]

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
            mr.increment('skip-due-to-empty')
            continue

        # Don't process events we've already looked at, or don't need to look at.
        # This doesn't happen with the mapreduce that pre-filters them out,
        # but it does happen when we scrape users potential events and throw them all in here.
        if pe.looked_at:
            logging.info('Already looked at event (added, or manually discarded), so no need to re-process.')
            mr.increment('skip-due-to-looked-at')
            continue

        event_id = pe.fb_event_id
        if not re.match(r'^\d+$', event_id):
            logging.error('Found a very strange potential event id: %s', event_id)
            mr.increment('skip-due-to-bad-id')
            continue

        new_pe_list.append(pe)
        new_fb_list.append(fb_event)
    return really_classify_events(fbl, new_pe_list, new_fb_list)

def really_classify_events(fbl, new_pe_list, new_fb_list, allow_posting=True):
    if not new_pe_list:
        new_pe_list = [None] * len(new_fb_list)
    logging.info('Filtering out already-added events and others, have %s remaining events to run the classifier on', len(new_fb_list))
    fb_event_ids = [x['info']['id'] for x in new_fb_list]
    fb_attending_maybe_list = fbl.get_multi(fb_api.LookupEventAttendingMaybe, fb_event_ids, allow_fail=True)

    results = []
    for pe, fb_event, fb_event_attending_maybe in zip(new_pe_list, new_fb_list, fb_attending_maybe_list):
        event_id = fb_event['info']['id']
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
            good_event = event_attendee_classifier.is_good_event_by_attendees(
                fbl,
                fb_event,
                fb_event_attending_maybe=fb_event_attending_maybe,
                classified_event=classified_event
            )
            logging.info('Is Good Event By Attendees: %s: %s', event_id, good_event)
            method = eventdata.CM_AUTO_ATTENDEE
        if good_event:
            result = '+%s\n' % '\t'.join((event_id, fb_event['info'].get('name', '')))
            try:
                invite_ids = pe.get_invite_uids() if pe else []
                logging.info('VTFI %s: Adding event %s, due to pe-invite-ids: %s', event_id, event_id, invite_ids)
                e = add_entities.add_update_event(fb_event, fbl, visible_to_fb_uids=invite_ids, creating_method=method, allow_posting=allow_posting)
                pe2 = potential_events.PotentialEvent.get_by_key_name(event_id)
                pe2.looked_at = True
                pe2.auto_looked_at = True
                pe2.put()
                # TODO(lambert): handle un-add-able events differently
                results.append(result)
                mr.increment('auto-added-dance-events')
                if e.start_time < datetime.datetime.now():
                    mr.increment('auto-added-dance-events-past')
                    mr.increment('auto-added-dance-events-past-eventid-%s' % event_id)
                else:
                    mr.increment('auto-added-dance-events-future')
            except fb_api.NoFetchedDataException as e:
                logging.error("Error adding event %s, no fetched data: %s", event_id, e)
            except add_entities.AddEventException as e:
                logging.warning("Error adding event %s, no fetched data: %s", event_id, e)
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

def maybe_add_events(fbl, event_ids):
    fb_events = fbl.get_multi(fb_api.LookupEvent, event_ids)
    empty_ids = [eid for x, eid in zip(fb_events, event_ids) if x['empty']]
    logging.info('Found empty ids: %s', empty_ids)
    fb_events = [x for x in fb_events if x and not x['empty']]
    return really_classify_events(fbl, None, fb_events, allow_posting=False)
