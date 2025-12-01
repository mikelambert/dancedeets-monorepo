"""
Cloud Run Job: Classify potential events using ML prediction.

Migrated from: dancedeets/ml/mr_prediction.py

This job uses a trained ML model to classify potential events and
score them as likely dance events.

Usage:
    python -m dancedeets.jobs.runner --job=classify_events_ml
"""

import logging
from typing import Optional

from dancedeets import fb_api
from dancedeets.event_scraper import potential_events
from dancedeets.jobs.base import BatchJob, JobRunner
from dancedeets.jobs.fb_utils import FBJobContext, get_multiple_tokens
from dancedeets.jobs.gcs_output import GCSOutputWriter, DEFAULT_BUCKET
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.ml import gprediction

logger = logging.getLogger(__name__)


class ClassifyEventsMLJob(BatchJob):
    """
    Job that classifies potential events using ML prediction.

    Uses Google Prediction API to score events as likely dance events.
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
        self._predict_service = None
        logger.info("ClassifyEventsMLJob initialized")

    @property
    def predict_service(self):
        """Lazy-loaded prediction service."""
        if self._predict_service is None:
            self._predict_service = gprediction.get_predict_service()
        return self._predict_service

    def setup(self) -> None:
        """Initialize the output writer."""
        if not self.dry_run:
            self.output_writer = GCSOutputWriter(
                bucket_name=self.bucket_name,
                blob_name='ml/classification_results.txt',
                content_type='text/plain',
            )

    def run_batch(self, pe_list: list) -> None:
        """Process a batch of potential events."""
        # Filter to events with match_score > 0
        pe_list = [x for x in pe_list if x.match_score > 0]
        if not pe_list:
            self.metrics.increment('batches_empty')
            return

        if not self.fb_context:
            logger.warning("No FB context, skipping batch")
            self.metrics.increment('batches_skipped_no_fb')
            return

        fbl = self.fb_context.get_fblookup()

        # Get events that don't already have scores
        pe_ids = [x.fb_event_id for x in pe_list if not getattr(x, 'dance_bias_score', None)]
        if pe_ids:
            fbl.request_multi(fb_api.LookupEvent, pe_ids)
            fbl.request_multi(fb_api.LookupEventAttending, pe_ids)

            try:
                fbl.batch_fetch()
            except Exception as e:
                logger.error(f"Error fetching Facebook data: {e}")
                self.metrics.increment('batches_failed_fb')
                return

        results = []
        for pe in pe_list:
            if not getattr(pe, 'dance_bias_score', None):
                try:
                    fb_event = fbl.fetched_data(fb_api.LookupEvent, pe.fb_event_id)
                    fb_event_attending = fbl.fetched_data(fb_api.LookupEventAttending, pe.fb_event_id)
                except fb_api.NoFetchedDataException:
                    self.metrics.increment('events_skipped_no_data')
                    continue

                if fb_event.get('empty'):
                    self.metrics.increment('events_skipped_empty')
                    continue

                # Score the event
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would classify event {pe.fb_event_id}")
                    self.metrics.increment('events_would_classify')
                else:
                    pe = potential_events.update_scores_for_potential_event(
                        pe, fb_event, fb_event_attending, self.predict_service
                    )
                    self.metrics.increment('events_classified')

            logger.debug(
                f"{pe.fb_event_id}: ms={pe.match_score}, "
                f"d={pe.dance_bias_score}, nd={pe.non_dance_bias_score}"
            )

            # Report events with high scores in both models
            if (getattr(pe, 'dance_bias_score', 0) or 0) > 0.5 and \
               (getattr(pe, 'non_dance_bias_score', 0) or 0) > 0.5:
                result = f"{pe.fb_event_id}:{pe.match_score}:{pe.dance_bias_score}:{pe.non_dance_bias_score}\n"
                results.append(result)
                self.metrics.increment('events_high_score')

        # Write results
        if results and not self.dry_run:
            for result in results:
                self.output_writer.write(result)

        self.metrics.increment('batches_processed')

    def teardown(self) -> None:
        """Finalize the output."""
        if not self.dry_run and self.output_writer:
            uri = self.output_writer.flush()
            logger.info(f"Classification results written to {uri}")


def main(dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the classify_events_ml job.

    Args:
        dry_run: If True, don't actually classify or save
    """
    logger.info("Starting classify_events_ml job")

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

    job = ClassifyEventsMLJob(
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
        batch_size=20,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
