"""
Cloud Run Job: Update source statistics.

Migrated from: dancedeets/event_scraper/thing_db.py (mr_count_potential_events)

This job counts potential events, real events, and false negatives
per source (fan pages, profiles, etc.) for source quality tracking.

Usage:
    python -m dancedeets.jobs.runner --job=update_source_stats
"""

import json
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from dancedeets.events import eventdata
from dancedeets.event_scraper import thing_db
from dancedeets.jobs.base import Job, JobRunner
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics

logger = logging.getLogger(__name__)


class UpdateSourceStatsJob(Job):
    """
    Job that updates source statistics.

    For each potential event, counts:
    - Whether it's a potential event (match_score > 0)
    - Whether it became a real event (exists in DBEvent)
    - Whether it's a false negative (real but not potential)

    Aggregates by source and updates Source entities.
    """

    def __init__(self, dry_run: bool = False):
        super().__init__()
        self.dry_run = dry_run

        # Aggregate counts per source: source_id -> (potential, real, false_negative, total)
        self.source_counts: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {'all': 0, 'potential': 0, 'real': 0, 'false_negative': 0}
        )

        logger.info("UpdateSourceStatsJob initialized")

    def run(self, pe) -> None:
        """Process a single potential event."""
        # Check if this became a real event
        db_event = eventdata.DBEvent.get_by_id(pe.fb_event_id)

        is_potential_event = pe.match_score > 0
        real_event = db_event is not None
        false_negative = bool(db_event and not is_potential_event)

        # Aggregate for each source
        for source_id in pe.source_ids_only():
            source_id_str = str(source_id)
            self.source_counts[source_id_str]['all'] += 1
            if is_potential_event:
                self.source_counts[source_id_str]['potential'] += 1
            if real_event:
                self.source_counts[source_id_str]['real'] += 1
            if false_negative:
                self.source_counts[source_id_str]['false_negative'] += 1

        self.metrics.increment('events_processed')

    def teardown(self) -> None:
        """Update all Source entities with aggregated counts."""
        logger.info(f"Updating {len(self.source_counts)} sources")

        sources_updated = 0
        sources_not_found = 0

        for source_id, counts in self.source_counts.items():
            source = thing_db.Source.get_by_key_name(source_id)
            if not source:
                logger.debug(f"Source not found: {source_id}")
                sources_not_found += 1
                continue

            if self.dry_run:
                logger.debug(
                    f"[DRY RUN] Would update source {source_id}: "
                    f"all={counts['all']}, potential={counts['potential']}, "
                    f"real={counts['real']}, false_negative={counts['false_negative']}"
                )
            else:
                source.num_all_events = counts['all']
                source.num_potential_events = counts['potential']
                source.num_real_events = counts['real']
                source.num_false_negatives = counts['false_negative']
                source.put()

            sources_updated += 1

        self.metrics.increment('sources_updated', sources_updated)
        self.metrics.increment('sources_not_found', sources_not_found)

        if self.dry_run:
            logger.info(f"[DRY RUN] Would update {sources_updated} sources")
        else:
            logger.info(f"Updated {sources_updated} sources")


def main(dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the update_source_stats job.

    Args:
        dry_run: If True, don't update sources
    """
    logger.info("Starting update_source_stats job")

    job = UpdateSourceStatsJob(dry_run=dry_run)
    set_current_metrics(job.metrics)

    runner = JobRunner(job)
    runner.run_from_datastore(
        entity_kind='dancedeets.event_scraper.potential_events.PotentialEvent',
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
