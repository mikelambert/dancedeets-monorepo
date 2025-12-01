"""
Cloud Run Job: Automatically add dance events to the database.

Migrated from: dancedeets/event_scraper/auto_add.py

This job classifies potential events using NLP and attendee analysis,
and automatically adds those that qualify as dance events.

Usage:
    python -m dancedeets.jobs.runner --job=auto_add_events
    python -m dancedeets.jobs.runner --job=auto_add_events --dancey_only=true
"""

import datetime
import logging
import re
from typing import List, Optional

from dancedeets import fb_api
from dancedeets.event_attendees import event_attendee_classifier
from dancedeets.events import eventdata
from dancedeets.jobs.base import BatchJob, JobRunner
from dancedeets.jobs.fb_utils import FBJobContext, get_multiple_tokens
from dancedeets.jobs.gcs_output import GCSOutputWriter, DEFAULT_BUCKET
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.nlp import event_auto_classifier
from dancedeets.nlp import event_classifier
from dancedeets.nlp.styles import street
from dancedeets.event_scraper import add_entities
from dancedeets.event_scraper import potential_events

logger = logging.getLogger(__name__)


class AutoAddEventsJob(BatchJob):
    """
    Job that automatically classifies and adds dance events.

    For each potential event:
    1. Fetch event data from Facebook
    2. Run NLP classifier on event text
    3. If text doesn't match, check attendee profiles
    4. Add qualifying events to the database
    """

    def __init__(
        self,
        fb_context: Optional[FBJobContext] = None,
        bucket_name: str = DEFAULT_BUCKET,
        allow_posting: bool = True,
        dry_run: bool = False,
    ):
        # Use small batch size to avoid timeouts (complex classification)
        super().__init__(batch_size=10)
        self.fb_context = fb_context
        self.bucket_name = bucket_name
        self.allow_posting = allow_posting
        self.dry_run = dry_run
        self.output_writer = None
        logger.info("AutoAddEventsJob initialized")

    def setup(self) -> None:
        """Initialize the output writer."""
        if not self.dry_run:
            self.output_writer = GCSOutputWriter(
                bucket_name=self.bucket_name,
                blob_name='auto_add/results.txt',
                content_type='text/plain',
            )

    def run_batch(self, pe_list: list) -> None:
        """Process a batch of potential events."""
        if not self.fb_context:
            logger.warning("No FB context, skipping batch")
            self.metrics.increment('batches_skipped_no_fb')
            return

        fbl = self.fb_context.get_fblookup()

        # Fetch event data from Facebook
        fb_list = fbl.get_multi(
            fb_api.LookupEvent,
            [x.fb_event_id for x in pe_list],
            allow_fail=True,
        )

        # Filter and classify events
        results = self._classify_events(fbl, pe_list, fb_list)

        # Write results
        if results and not self.dry_run:
            for result in results:
                self.output_writer.write(result)

        self.metrics.increment('batches_processed')

    def _classify_events(self, fbl, pe_list: list, fb_list: list) -> List[str]:
        """
        Filter and classify events.

        Returns:
            List of result strings for successfully added events
        """
        new_pe_list = []
        new_fb_list = []

        for pe, fb_event in zip(pe_list, fb_list):
            # Handle past events
            if pe.set_past_event(fb_event):
                if not self.dry_run:
                    pe.put()

            if not fb_event or fb_event.get('empty'):
                self.metrics.increment('skip-due-to-empty')
                continue

            # Skip already processed events
            if pe.looked_at:
                logger.debug('Already looked at event, skipping')
                self.metrics.increment('skip-due-to-looked-at')
                continue

            event_id = pe.fb_event_id
            if not re.match(r'^\d+$', event_id):
                logger.error(f'Found a very strange potential event id: {event_id}')
                self.metrics.increment('skip-due-to-bad-id')
                continue

            new_pe_list.append(pe)
            new_fb_list.append(fb_event)

        return self._really_classify_events(fbl, new_pe_list, new_fb_list)

    def _really_classify_events(self, fbl, pe_list: list, fb_list: list) -> List[str]:
        """
        Actually classify events and add qualifying ones.

        Returns:
            List of result strings
        """
        if not fb_list:
            return []

        if not pe_list:
            pe_list = [None] * len(fb_list)

        logger.info(f'Classifying {len(fb_list)} events')

        # Fetch attendee data
        fb_event_ids = [x['info']['id'] for x in fb_list]
        fb_attending_maybe_list = fbl.get_multi(
            fb_api.LookupEventAttendingMaybe,
            fb_event_ids,
            allow_fail=True,
        )

        results = []
        for pe, fb_event, fb_event_attending_maybe in zip(pe_list, fb_list, fb_attending_maybe_list):
            event_id = fb_event['info']['id']
            logger.debug(f'Classifying event {event_id}')

            # Run text classifier
            classified_event = event_classifier.get_classified_event(fb_event)
            auto_add_result = event_auto_classifier.is_auto_add_event(classified_event)
            logger.debug(f'Text classification result: {auto_add_result}')

            good_event = False
            method = None
            verticals = []

            if auto_add_result.is_good_event():
                good_event = True
                method = eventdata.CM_AUTO
                verticals = auto_add_result.verticals()
            elif fb_event_attending_maybe:
                # Try attendee-based classification
                logger.debug(f'Trying attendee classification for {event_id}')
                good_event = event_attendee_classifier.is_good_event_by_attendees(
                    fbl,
                    fb_event,
                    fb_event_attending_maybe=fb_event_attending_maybe,
                    classified_event=classified_event,
                )
                logger.debug(f'Attendee classification result: {good_event}')
                method = eventdata.CM_AUTO_ATTENDEE
                verticals = [street.Style.get_name()]

            if good_event:
                result = f"+{event_id}\t{fb_event['info'].get('name', '')}\n"

                if self.dry_run:
                    logger.info(f"[DRY RUN] Would add event {event_id}")
                    self.metrics.increment('events_would_add')
                    results.append(result)
                    continue

                try:
                    invite_ids = pe.get_invite_uids() if pe else []
                    logger.info(f'Adding event {event_id}, invite_ids: {invite_ids}')

                    e = add_entities.add_update_fb_event(
                        fb_event,
                        fbl,
                        visible_to_fb_uids=invite_ids,
                        creating_method=method,
                        allow_posting=self.allow_posting,
                        verticals=verticals,
                    )

                    # Mark as processed
                    pe2 = potential_events.PotentialEvent.get_by_key_name(event_id)
                    pe2.looked_at = True
                    pe2.auto_looked_at = True
                    pe2.put()

                    results.append(result)
                    self.metrics.increment('auto-added-dance-events')

                    # Track by time period
                    if e.start_time < datetime.datetime.now():
                        self.metrics.increment('auto-added-dance-events-past')
                    else:
                        self.metrics.increment('auto-added-dance-events-future')

                    # Track by vertical
                    for vertical in e.verticals:
                        self.metrics.increment(f'auto-added-vertical-{vertical}')

                except fb_api.NoFetchedDataException as e:
                    logger.error(f"Error adding event {event_id}, no fetched data: {e}")
                    self.metrics.increment('events_failed_no_data')
                except add_entities.AddEventException as e:
                    logger.warning(f"Error adding event {event_id}: {e}")
                    self.metrics.increment('events_failed_add')

        return results

    def teardown(self) -> None:
        """Finalize the output."""
        if not self.dry_run and self.output_writer:
            uri = self.output_writer.flush()
            logger.info(f"Results written to {uri}")


def main(
    dancey_only: bool = False,
    past_event: bool = None,
    dry_run: bool = False,
    **kwargs,
) -> None:
    """
    Main entry point for the auto_add_events job.

    Args:
        dancey_only: If True, only process events with should_look_at=True
        past_event: Filter by past_event status (True/False/None for all)
        dry_run: If True, don't actually add events
    """
    logger.info(f"Starting auto_add_events job: dancey_only={dancey_only}, past_event={past_event}")

    # Get tokens for Facebook API access
    try:
        tokens = get_multiple_tokens(token_count=50)
        logger.info(f"Got {len(tokens)} access tokens for rotation")
    except Exception as e:
        logger.warning(f"Could not get multiple tokens: {e}")
        tokens = []

    fb_context = FBJobContext(
        fb_uid='system',
        access_tokens=tokens,
        allow_cache=True,
    ) if tokens else None

    job = AutoAddEventsJob(
        fb_context=fb_context,
        dry_run=dry_run,
    )
    set_current_metrics(job.metrics)

    runner = JobRunner(job)

    # Build filters
    filters = []
    if dancey_only:
        filters.append(('should_look_at', '=', True))
    if past_event is not None:
        filters.append(('past_event', '=', past_event))

    runner.run_from_datastore_batched(
        entity_kind='dancedeets.event_scraper.potential_events.PotentialEvent',
        filters=filters,
        batch_size=10,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
