"""
Cloud Run Job: Scrape sources for events and classify them.

Migrated from: dancedeets/event_scraper/thing_scraper2.py

This job scrapes configured sources (fan pages, profiles, etc.) for
event listings, then classifies discovered events.

Usage:
    python -m dancedeets.jobs.runner --job=scrape_and_classify
    python -m dancedeets.jobs.runner --job=scrape_and_classify --min_potential_events=5
"""

import json
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Set

from dancedeets.jobs.base import BatchJob, JobRunner
from dancedeets.jobs.fb_utils import FBJobContext, get_multiple_tokens
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.event_scraper import event_pipeline
from dancedeets.event_scraper import potential_events
from dancedeets.event_scraper import thing_scraper

logger = logging.getLogger(__name__)


class ScrapeAndClassifyJob(BatchJob):
    """
    Job that scrapes sources and classifies discovered events.

    This combines the map and reduce steps from the original MapReduce:
    1. Map: Scrape each source for events
    2. Reduce: Group by event_id and process

    Uses in-memory aggregation since event volumes are manageable.
    """

    def __init__(
        self,
        fb_context: Optional[FBJobContext] = None,
        min_potential_events: int = 0,
        dry_run: bool = False,
    ):
        super().__init__(batch_size=20)
        self.fb_context = fb_context
        self.min_potential_events = min_potential_events
        self.dry_run = dry_run

        # Aggregate discovered events by event_id
        # event_id -> list of (source_id, source_field, extra_source_id)
        self.discovered_events: Dict[str, List[tuple]] = defaultdict(list)

        logger.info(f"ScrapeAndClassifyJob initialized with min_potential_events={min_potential_events}")

    def run_batch(self, sources: list) -> None:
        """Process a batch of sources (scraping phase)."""
        # Filter sources by min_potential_events
        if self.min_potential_events > 0:
            sources = [
                s for s in sources
                if (s.num_potential_events or 0) >= self.min_potential_events
            ]

        if not sources:
            self.metrics.increment('batches_empty')
            return

        if not self.fb_context:
            logger.warning("No FB context, skipping batch")
            self.metrics.increment('batches_skipped_no_fb')
            return

        fbl = self.fb_context.get_fblookup()
        fbl.allow_cache = False  # Don't cache during scraping
        # Make passthrough to avoid unnecessary memcache puts
        fbl.make_passthrough()

        # Discover events from sources
        try:
            discovered_list = thing_scraper.discover_events_from_sources(fbl, sources)
        except Exception as e:
            logger.error(f"Error scraping sources: {e}")
            self.metrics.increment('batches_failed_scrape')
            return

        # Aggregate by event_id
        for discovered in discovered_list:
            state = (
                discovered.source_id,
                discovered.source_field,
                discovered.extra_source_id,
            )
            self.discovered_events[discovered.event_id].append(state)
            self.metrics.increment('events_discovered')

        self.metrics.increment('sources_scraped', len(sources))
        self.metrics.increment('batches_processed')

    def teardown(self) -> None:
        """Process all discovered events (reduce phase)."""
        logger.info(f"Processing {len(self.discovered_events)} unique events")

        if self.dry_run:
            logger.info("[DRY RUN] Would process discovered events")
            for event_id, sources in list(self.discovered_events.items())[:10]:
                logger.info(f"  Event {event_id}: {len(sources)} sources")
            return

        if not self.fb_context:
            logger.warning("No FB context, skipping event processing")
            return

        fbl = self.fb_context.get_fblookup()
        fbl.allow_cache = True  # Use cache for classification

        # Process events in batches
        events_processed = 0
        events_failed = 0

        for event_id, source_list in self.discovered_events.items():
            try:
                # Build discovered event objects
                discovered_list = []
                for source_id, source_field, extra_source_id in source_list:
                    discovered = potential_events.DiscoveredEvent(
                        event_id, None, source_field, extra_source_id
                    )
                    discovered.source = None
                    discovered.source_id = source_id
                    discovered_list.append(discovered)

                # Process through event pipeline
                event_pipeline.process_discovered_events(fbl, discovered_list)
                events_processed += 1

            except Exception as e:
                logger.error(f"Error processing event {event_id}: {e}")
                events_failed += 1

        self.metrics.increment('events_processed', events_processed)
        self.metrics.increment('events_failed', events_failed)
        logger.info(f"Processed {events_processed} events, {events_failed} failed")


def main(
    min_potential_events: int = 0,
    dry_run: bool = False,
    **kwargs,
) -> None:
    """
    Main entry point for the scrape_and_classify job.

    Args:
        min_potential_events: Only scrape sources with at least this many potential events
        dry_run: If True, don't actually process events
    """
    logger.info(f"Starting scrape_and_classify job with min_potential_events={min_potential_events}")

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
        allow_cache=False,
    ) if tokens else None

    job = ScrapeAndClassifyJob(
        fb_context=fb_context,
        min_potential_events=min_potential_events,
        dry_run=dry_run,
    )
    set_current_metrics(job.metrics)

    runner = JobRunner(job)
    runner.run_from_datastore_batched(
        entity_kind='dancedeets.event_scraper.thing_db.Source',
        batch_size=20,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
