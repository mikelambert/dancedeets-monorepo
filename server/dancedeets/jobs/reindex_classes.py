"""
Cloud Run Job: Reindex dance classes in search.

Migrated from: dancedeets/classes/class_pipeline.py (ReindexClasses)

This job rebuilds the dance class search index from scraped data.

Usage:
    python -m dancedeets.jobs.runner --job=reindex_classes
"""

import logging

from dancedeets.classes import class_index
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics

logger = logging.getLogger(__name__)


def main(dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the reindex_classes job.

    Args:
        dry_run: If True, don't actually reindex
    """
    logger.info("Starting reindex_classes job")

    metrics = JobMetrics()
    set_current_metrics(metrics)

    if dry_run:
        logger.info("[DRY RUN] Would rebuild class index")
        metrics.increment('reindex_skipped')
    else:
        logger.info("Rebuilding class index...")
        try:
            class_index.StudioClassIndex.rebuild_from_query()
            logger.info("Class index rebuilt successfully")
            metrics.increment('reindex_completed')
        except Exception as e:
            logger.error(f"Error rebuilding class index: {e}")
            metrics.increment('reindex_failed')
            raise

    metrics.log_summary()


if __name__ == '__main__':
    main()
