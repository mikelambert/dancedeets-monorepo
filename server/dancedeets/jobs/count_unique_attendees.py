"""
Cloud Run Job: Count unique attendees per city.

Migrated from: dancedeets/logic/unique_attendees.py

This job counts unique RSVPs across all events, grouped by city and country.

Usage:
    python -m dancedeets.jobs.runner --job=count_unique_attendees
"""

import logging
from collections import defaultdict
from typing import Dict, Optional, Set

from dancedeets import fb_api
from dancedeets.jobs.base import BatchJob, JobRunner
from dancedeets.jobs.fb_utils import FBJobContext, get_multiple_tokens
from dancedeets.jobs.gcs_output import GCSOutputWriter, DEFAULT_BUCKET
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics

logger = logging.getLogger(__name__)

BATCH_SIZE = 20


class CountUniqueAttendeesJob(BatchJob):
    """
    Job that counts unique attendees per city/country.

    This is a "reduce" style job that aggregates attendees across all events.
    Uses in-memory aggregation instead of MapReduce framework.
    """

    def __init__(
        self,
        fb_context: Optional[FBJobContext] = None,
        bucket_name: str = DEFAULT_BUCKET,
        dry_run: bool = False,
    ):
        super().__init__(batch_size=BATCH_SIZE)
        self.fb_context = fb_context
        self.bucket_name = bucket_name
        self.dry_run = dry_run
        self.output_writer = None

        # In-memory aggregation (replaces MapReduce reduce step)
        # Maps location -> set of attendee IDs
        self.city_attendees: Dict[str, Set[str]] = defaultdict(set)
        self.country_attendees: Dict[str, Set[str]] = defaultdict(set)

        # For counting total RSVPs (not unique)
        self.city_rsvp_count: Dict[str, int] = defaultdict(int)
        self.country_rsvp_count: Dict[str, int] = defaultdict(int)

        logger.info("CountUniqueAttendeesJob initialized")

    def setup(self) -> None:
        """Initialize the output writer."""
        if not self.dry_run:
            self.output_writer = GCSOutputWriter(
                bucket_name=self.bucket_name,
                blob_name='analytics/unique_attendees.txt',
                content_type='text/plain',
            )

    def run_batch(self, db_events: list) -> None:
        """Process a batch of events."""
        # Filter to Facebook events only
        db_events = [x for x in db_events if x.is_fb_event]
        if not db_events:
            self.metrics.increment('batches_empty')
            return

        if not self.fb_context:
            logger.warning("No FB context, skipping batch")
            self.metrics.increment('batches_skipped_no_fb')
            return

        fbl = self.fb_context.get_fblookup()

        # Request attending data
        fbl.request_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in db_events])

        try:
            fbl.batch_fetch()
        except Exception as e:
            logger.error(f"Error fetching Facebook data: {e}")
            self.metrics.increment('batches_failed_fb')
            return

        for db_event in db_events:
            try:
                fb_event_attending = fbl.fetched_data(
                    fb_api.LookupEventAttending, db_event.id
                )
            except fb_api.NoFetchedDataException:
                logger.warning(f'No attending found for {db_event.id}')
                self.metrics.increment('events_no_attending')
                continue

            if fb_event_attending.get('empty'):
                self.metrics.increment('events_empty_attending')
                continue

            attendees = fb_event_attending.get('attending', {}).get('data', [])
            city = db_event.city_name
            country = db_event.country

            for attendee in attendees:
                attendee_id = attendee['id']

                if city:
                    self.city_attendees[city].add(attendee_id)
                    self.city_rsvp_count[city] += 1

                if country:
                    self.country_attendees[country].add(attendee_id)
                    self.country_rsvp_count[country] += 1

            self.metrics.increment('events_processed')
            self.metrics.increment('attendees_processed', len(attendees))

        self.metrics.increment('batches_processed')

    def teardown(self) -> None:
        """Write final results."""
        if self.dry_run:
            logger.info("[DRY RUN] Would write attendee counts")
            logger.info(f"  Cities: {len(self.city_attendees)}")
            logger.info(f"  Countries: {len(self.country_attendees)}")
            return

        # Write city results
        for city in sorted(self.city_attendees.keys()):
            unique_count = len(self.city_attendees[city])
            total_count = self.city_rsvp_count[city]
            self.output_writer.write(f"Unique Attendees in City: {city}: {unique_count}")
            self.output_writer.write(f"Total RSVPs in City: {city}: {total_count}")

        # Write country results
        for country in sorted(self.country_attendees.keys()):
            unique_count = len(self.country_attendees[country])
            total_count = self.country_rsvp_count[country]
            self.output_writer.write(f"Unique Attendees in Country: {country}: {unique_count}")
            self.output_writer.write(f"Total RSVPs in Country: {country}: {total_count}")

        uri = self.output_writer.flush()
        logger.info(f"Results written to {uri}")

        # Log summary
        total_unique = sum(len(s) for s in self.city_attendees.values())
        logger.info(f"Total unique attendees across all cities: {total_unique}")


def main(dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the count_unique_attendees job.

    Args:
        dry_run: If True, don't write to GCS
    """
    logger.info("Starting count_unique_attendees job")

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

    job = CountUniqueAttendeesJob(
        fb_context=fb_context,
        dry_run=dry_run,
    )
    set_current_metrics(job.metrics)

    runner = JobRunner(job)
    runner.run_from_datastore_batched(
        entity_kind='dancedeets.events.eventdata.DBEvent',
        batch_size=BATCH_SIZE,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
