"""
Cloud Run Job: Generate ML training data from potential events.

Migrated from: dancedeets/ml/gprediction.py

This job generates training data for the ML classifier by extracting
features from potential events and writing them to GCS.

Usage:
    python -m dancedeets.jobs.runner --job=generate_training_data
"""

import csv
import io
import logging
import string
from typing import Optional

from dancedeets import fb_api
from dancedeets.events import eventdata
from dancedeets.events import event_locations
from dancedeets.jobs.base import BatchJob, JobRunner
from dancedeets.jobs.fb_utils import FBJobContext, get_multiple_tokens
from dancedeets.jobs.gcs_output import GCSOutputWriter, DEFAULT_BUCKET
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics

logger = logging.getLogger(__name__)

# Character translation for stripping punctuation
convert_chars = string.punctuation + '\r\n\t'
trans = str.maketrans(convert_chars, ' ' * len(convert_chars))


def strip_punctuation(s: str) -> str:
    """Remove punctuation from a string."""
    return s.translate(trans)


def get_training_features(potential_event, fb_event, fb_event_attending) -> tuple:
    """
    Extract training features from an event.

    Returns:
        Tuple of feature values
    """
    if 'owner' in fb_event['info']:
        owner_name = 'id%s' % fb_event['info']['owner']['id']
    else:
        owner_name = ''

    location = event_locations.get_address_for_fb_event(fb_event)

    def strip_text(s):
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return strip_punctuation(s).lower()

    name = strip_text(fb_event['info'].get('name', ''))
    description = strip_text(fb_event['info'].get('description', ''))

    attendee_list = ' '.join([
        'id%s' % x['id']
        for x in fb_event_attending.get('attending', {}).get('data', [])
    ])

    source_list = ' '.join(
        'id%s' % x.id
        for x in potential_event.source_ids_only()
    )

    # Currently only returning attendee_list (as per original code)
    return (attendee_list,)
    # Full features would be:
    # return (potential_event.language, owner_name, location, name, description, attendee_list, source_list)


class GenerateTrainingDataJob(BatchJob):
    """
    Job that generates ML training data from potential events.

    Extracts features from events and writes CSV training data to GCS.
    """

    def __init__(
        self,
        fb_context: Optional[FBJobContext] = None,
        bucket_name: str = DEFAULT_BUCKET,
        dry_run: bool = False,
    ):
        super().__init__(batch_size=20)
        self.fb_context = fb_context
        self.bucket_name = bucket_name
        self.dry_run = dry_run
        self.output_writer = None
        logger.info("GenerateTrainingDataJob initialized")

    def setup(self) -> None:
        """Initialize the output writer."""
        if not self.dry_run:
            self.output_writer = GCSOutputWriter(
                bucket_name=self.bucket_name,
                blob_name='ml/training_data.csv',
                content_type='text/csv',
            )

    def run_batch(self, pevents: list) -> None:
        """Process a batch of potential events."""
        if not self.fb_context:
            logger.warning("No FB context, skipping batch")
            self.metrics.increment('batches_skipped_no_fb')
            return

        fbl = self.fb_context.get_fblookup()
        fbl.allow_memcache_write = False  # Don't pollute memcache

        # Only process events that have been looked at
        fb_event_ids = [x.fb_event_id for x in pevents if x.looked_at]
        if not fb_event_ids:
            self.metrics.increment('batches_empty')
            return

        # Fetch from Facebook
        fbl.request_multi(fb_api.LookupEvent, fb_event_ids)
        fbl.request_multi(fb_api.LookupEventAttending, fb_event_ids)

        try:
            fbl.batch_fetch()
        except Exception as e:
            logger.error(f"Error fetching Facebook data: {e}")
            self.metrics.increment('batches_failed_fb')
            return

        # Get existing events to determine labels
        good_event_ids = [
            x.fb_event_id
            for x in eventdata.DBEvent.get_by_ids(fb_event_ids, keys_only=True)
            if x
        ]

        # Build CSV
        csv_file = io.StringIO()
        csv_writer = csv.writer(csv_file)

        for potential_event in pevents:
            if not potential_event.looked_at:
                continue

            try:
                # Label: 'dance' if event exists in DB, 'nodance' otherwise
                label = 'dance' if potential_event.fb_event_id in good_event_ids else 'nodance'

                fb_event = fbl.fetched_data(fb_api.LookupEvent, potential_event.fb_event_id)
                if fb_event.get('empty'):
                    self.metrics.increment('events_skipped_empty')
                    continue

                fb_event_attending = fbl.fetched_data(
                    fb_api.LookupEventAttending,
                    potential_event.fb_event_id
                )

                training_features = get_training_features(
                    potential_event, fb_event, fb_event_attending
                )
                csv_writer.writerow([label] + list(training_features))
                self.metrics.increment('rows_written')

            except fb_api.NoFetchedDataException:
                logger.debug(f"No data fetched for event id {potential_event.fb_event_id}")
                self.metrics.increment('events_skipped_no_data')

        # Write to GCS
        output = csv_file.getvalue()
        if output:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would write training data to GCS")
            else:
                self.output_writer.write(output)

        self.metrics.increment('batches_processed')

    def teardown(self) -> None:
        """Finalize the output."""
        if not self.dry_run and self.output_writer:
            uri = self.output_writer.flush()
            logger.info(f"Training data written to {uri}")


def main(dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the generate_training_data job.

    Args:
        dry_run: If True, don't write to GCS
    """
    logger.info("Starting generate_training_data job")

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

    job = GenerateTrainingDataJob(
        fb_context=fb_context,
        dry_run=dry_run,
    )
    set_current_metrics(job.metrics)

    runner = JobRunner(job)
    runner.run_from_datastore_batched(
        entity_kind='dancedeets.event_scraper.potential_events.PotentialEvent',
        batch_size=20,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
