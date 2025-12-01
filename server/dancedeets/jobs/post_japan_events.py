"""
Cloud Run Job: Post future Japan events to social media.

Migrated from: dancedeets/pubsub/pubsub_tasks.py

This job finds all future dance events in Japan and publishes them
to configured social media accounts.

Usage:
    python -m dancedeets.jobs.runner --job=post_japan_events
    python -m dancedeets.jobs.runner --job=post_japan_events --token_nickname=twitter_jp
"""

import logging

from dancedeets.jobs.base import BatchJob, JobRunner
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.pubsub import pubsub
from dancedeets.util import dates

logger = logging.getLogger(__name__)


class PostJapanEventsJob(BatchJob):
    """
    Job that posts Japan events to social media.

    Processes events in batches, filtering to only those in Japan,
    then publishes each to social media via the pubsub module.
    """

    def __init__(self, token_nickname: str = None, dry_run: bool = False):
        super().__init__(batch_size=20)
        self.token_nickname = token_nickname
        self.dry_run = dry_run
        logger.info(f"PostJapanEventsJob initialized with token_nickname={token_nickname}")

    def run_batch(self, db_events: list) -> None:
        """Process a batch of events."""
        # Filter to Japan events
        japan_events = [
            event for event in db_events
            if event.actual_city_name and event.actual_city_name.endswith('Japan')
        ]

        logger.info(f"Batch: {len(db_events)} events, {len(japan_events)} in Japan")
        self.metrics.increment('events_total', len(db_events))
        self.metrics.increment('events_in_japan', len(japan_events))

        for db_event in japan_events:
            try:
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would publish event {db_event.id}")
                    self.metrics.increment('events_would_publish')
                else:
                    pubsub.eventually_publish_event(db_event.id, self.token_nickname)
                    self.metrics.increment('events_published')
            except Exception as e:
                logger.error(f"Error publishing event {db_event.id}: {e}")
                self.metrics.increment('events_failed')


def main(token_nickname: str = None, dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the post_japan_events job.

    Args:
        token_nickname: Optional social media token nickname to use
        dry_run: If True, don't actually publish events
    """
    logger.info(f"Starting post_japan_events job")

    job = PostJapanEventsJob(token_nickname=token_nickname, dry_run=dry_run)
    set_current_metrics(job.metrics)

    runner = JobRunner(job)

    # Query future events
    filters = [
        ('search_time_period', '=', dates.TIME_FUTURE),
    ]

    runner.run_from_datastore_batched(
        entity_kind='dancedeets.events.eventdata.DBEvent',
        filters=filters,
        batch_size=20,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
