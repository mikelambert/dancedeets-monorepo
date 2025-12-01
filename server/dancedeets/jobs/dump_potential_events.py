"""
Cloud Run Job: Dump potential events data to GCS.

Migrated from: dancedeets/logic/mr_dump.py

This job exports potential event data (from Facebook API) to CSV format
in Google Cloud Storage for analysis or ML training.

Usage:
    python -m dancedeets.jobs.runner --job=dump_potential_events
"""

import csv
import io
import json
import logging
from typing import Optional

from dancedeets import fb_api
from dancedeets.jobs.base import BatchJob, JobRunner
from dancedeets.jobs.fb_utils import FBJobContext, get_multiple_tokens
from dancedeets.jobs.gcs_output import GCSOutputWriter, DEFAULT_BUCKET
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics

logger = logging.getLogger(__name__)


class DumpPotentialEventsJob(BatchJob):
    """
    Job that dumps potential event data to GCS.

    Fetches event data from Facebook and writes as CSV.
    """

    def __init__(
        self,
        fb_context: Optional[FBJobContext] = None,
        bucket_name: str = DEFAULT_BUCKET,
        dry_run: bool = False,
    ):
        super().__init__(batch_size=80)
        self.fb_context = fb_context
        self.bucket_name = bucket_name
        self.dry_run = dry_run
        self.output_writer = None
        logger.info("DumpPotentialEventsJob initialized")

    def setup(self) -> None:
        """Initialize the output writer."""
        if not self.dry_run:
            self.output_writer = GCSOutputWriter(
                bucket_name=self.bucket_name,
                blob_name='exports/potential_events.csv',
                content_type='text/csv',
            )

    def run_batch(self, pe_list: list) -> None:
        """Process a batch of potential events."""
        # Filter to events with match_score > 0
        pe_list = [x for x in pe_list if x.match_score > 0]
        if not pe_list:
            self.metrics.increment('batches_empty')
            return

        # Get Facebook lookup
        if not self.fb_context:
            logger.warning("No FB context, skipping batch")
            self.metrics.increment('batches_skipped_no_fb')
            return

        fbl = self.fb_context.get_fblookup()

        # Request event data from Facebook
        fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in pe_list])

        try:
            fbl.batch_fetch()
        except Exception as e:
            logger.error(f"Error fetching Facebook data: {e}")
            self.metrics.increment('batches_failed_fb')
            return

        # Build CSV output
        csv_file = io.StringIO()
        csv_writer = csv.writer(csv_file)

        for pe in pe_list:
            try:
                result = json.dumps(fbl.fetched_data(fb_api.LookupEvent, pe.fb_event_id))
                cache_key = fbl.key_to_cache_key(
                    fb_api.generate_key(fb_api.LookupEvent, pe.fb_event_id)
                )
                csv_writer.writerow([cache_key, result])
                self.metrics.increment('events_exported')
            except fb_api.NoFetchedDataException:
                logger.error(f"Skipping row for event id {pe.fb_event_id}")
                self.metrics.increment('events_skipped_no_data')

        # Write to GCS
        if self.dry_run:
            logger.info(f"[DRY RUN] Would write {len(pe_list)} events to GCS")
        else:
            self.output_writer.write(csv_file.getvalue())

        self.metrics.increment('batches_processed')

    def teardown(self) -> None:
        """Finalize the output."""
        if not self.dry_run and self.output_writer:
            uri = self.output_writer.flush()
            logger.info(f"Export written to {uri}")


def main(dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the dump_potential_events job.

    Args:
        dry_run: If True, don't write to GCS
    """
    logger.info("Starting dump_potential_events job")

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
        allow_cache=False,  # Don't pollute cache with this data
    ) if tokens else None

    job = DumpPotentialEventsJob(
        fb_context=fb_context,
        dry_run=dry_run,
    )
    set_current_metrics(job.metrics)

    runner = JobRunner(job)

    # Only process events that haven't been looked at
    filters = [
        ('looked_at', '=', None),
    ]

    runner.run_from_datastore_batched(
        entity_kind='dancedeets.event_scraper.potential_events.PotentialEvent',
        filters=filters,
        batch_size=80,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
