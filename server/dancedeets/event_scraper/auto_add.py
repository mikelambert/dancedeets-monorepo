"""
Auto-add event classification logic.

The batch processing has been migrated to Cloud Run Jobs.
See: dancedeets.jobs.auto_add_events

This module retains:
- classify_events: Filter and classify potential events
- really_classify_events: Core classification and adding logic
- maybe_add_events: Add events by IDs (for non-batch contexts)
"""
import datetime
import logging
import re

from dancedeets import fb_api

from dancedeets.event_attendees import event_attendee_classifier
from dancedeets.events import eventdata
from dancedeets.nlp import event_auto_classifier
from dancedeets.nlp import event_classifier
from dancedeets.nlp.styles import street
from . import add_entities
from . import potential_events


def is_good_event_by_text(fb_event, classified_event):
    """Check if event is a good dance event based on text classification."""
    return event_auto_classifier.is_auto_add_event(classified_event).is_good_event()


def classify_events(fbl, pe_list, fb_list, metrics=None):
    """
    Filter and classify potential events.

    Args:
        fbl: Facebook batch lookup
        pe_list: List of PotentialEvent objects
        fb_list: List of Facebook event data
        metrics: Optional metrics counter (for Cloud Run Jobs)

    Returns:
        List of result strings for added events
    """
    new_pe_list = []
    new_fb_list = []
    # Go through and find all potential events we actually want to attempt to classify
    for pe, fb_event in zip(pe_list, fb_list):
        # Get these past events out of the way, saved, then continue.
        if pe.set_past_event(fb_event):
            pe.put()

        if not fb_event or fb_event['empty']:
            if metrics:
                metrics.increment('skip-due-to-empty')
            continue

        # Don't process events we've already looked at, or don't need to look at.
        if pe.looked_at:
            logging.info('Already looked at event (added, or manually discarded), so no need to re-process.')
            if metrics:
                metrics.increment('skip-due-to-looked-at')
            continue

        event_id = pe.fb_event_id
        if not re.match(r'^\d+$', event_id):
            logging.error('Found a very strange potential event id: %s', event_id)
            if metrics:
                metrics.increment('skip-due-to-bad-id')
            continue

        new_pe_list.append(pe)
        new_fb_list.append(fb_event)
    return really_classify_events(fbl, new_pe_list, new_fb_list, metrics=metrics)


def really_classify_events(fbl, new_pe_list, new_fb_list, allow_posting=True, metrics=None):
    """
    Core classification logic - classify and add dance events.

    Args:
        fbl: Facebook batch lookup
        new_pe_list: List of PotentialEvent objects
        new_fb_list: List of Facebook event data
        allow_posting: Whether to post to social media
        metrics: Optional metrics counter (for Cloud Run Jobs)

    Returns:
        List of result strings for added events
    """
    if not new_pe_list:
        new_pe_list = [None] * len(new_fb_list)
    logging.info('Filtering out already-added events and others, have %s remaining events to run the classifier on', len(new_fb_list))
    fb_event_ids = [x['info']['id'] for x in new_fb_list]
    fb_attending_maybe_list = fbl.get_multi(fb_api.LookupEventAttendingMaybe, fb_event_ids, allow_fail=True)

    results = []
    for pe, fb_event, fb_event_attending_maybe in zip(new_pe_list, new_fb_list, fb_attending_maybe_list):
        event_id = fb_event['info']['id']
        logging.info('Is Good Event By Text: %s: Checking...', event_id)
        # And then classify it appropriately
        classified_event = event_classifier.get_classified_event(fb_event)
        auto_add_result = event_auto_classifier.is_auto_add_event(classified_event)
        logging.info('Is Good Event By Text: %s: %s', event_id, auto_add_result)
        good_event = False
        if auto_add_result.is_good_event():
            good_event = True
            method = eventdata.CM_AUTO
            verticals = auto_add_result.verticals()
        elif fb_event_attending_maybe:
            logging.info('Is Good Event By Attendees: %s: Checking...', event_id)
            good_event = event_attendee_classifier.is_good_event_by_attendees(
                fbl, fb_event, fb_event_attending_maybe=fb_event_attending_maybe, classified_event=classified_event
            )
            logging.info('Is Good Event By Attendees: %s: %s', event_id, good_event)
            method = eventdata.CM_AUTO_ATTENDEE
            verticals = [street.Style.get_name()]
        if good_event:
            result = '+%s\n' % '\t'.join((event_id, fb_event['info'].get('name', '')))
            try:
                invite_ids = pe.get_invite_uids() if pe else []
                logging.info('VTFI %s: Adding event %s, due to pe-invite-ids: %s', event_id, event_id, invite_ids)
                e = add_entities.add_update_fb_event(
                    fb_event,
                    fbl,
                    visible_to_fb_uids=invite_ids,
                    creating_method=method,
                    allow_posting=allow_posting,
                    verticals=verticals,
                )
                pe2 = potential_events.PotentialEvent.get_by_key_name(event_id)
                pe2.looked_at = True
                pe2.auto_looked_at = True
                pe2.put()
                results.append(result)
                if metrics:
                    metrics.increment('auto-added-dance-events')
                    if e.start_time < datetime.datetime.now():
                        metrics.increment('auto-added-dance-events-past')
                        for vertical in e.verticals:
                            metrics.increment('auto-added-dance-event-past-vertical-%s' % vertical)
                    else:
                        metrics.increment('auto-added-dance-events-future')
                        for vertical in e.verticals:
                            metrics.increment('auto-added-dance-event-future-vertical-%s' % vertical)
                    for vertical in e.verticals:
                        metrics.increment('auto-added-dance-event-vertical-%s' % vertical)
            except fb_api.NoFetchedDataException as e:
                logging.error("Error adding event %s, no fetched data: %s", event_id, e)
            except add_entities.AddEventException as e:
                logging.warning("Error adding event %s, no fetched data: %s", event_id, e)
    return results


def maybe_add_events(fbl, event_ids):
    """
    Attempt to add events by their IDs.

    Used for non-batch contexts where we have specific event IDs to check.

    Args:
        fbl: Facebook batch lookup
        event_ids: List of Facebook event IDs

    Returns:
        List of result strings for added events
    """
    fb_events = fbl.get_multi(fb_api.LookupEvent, event_ids)
    empty_ids = [eid for x, eid in zip(fb_events, event_ids) if x['empty']]
    logging.info('Found empty ids: %s', empty_ids)
    fb_events = [x for x in fb_events if x and not x['empty']]
    return really_classify_events(fbl, None, fb_events, allow_posting=False)
