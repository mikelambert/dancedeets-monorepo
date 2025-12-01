"""
Cloud Run Job: Start ScrapingHub spider jobs.

Migrated from: dancedeets/classes/class_pipeline.py (start_spiders)

This job triggers spider crawls on ScrapingHub for dance studio schedules.

Usage:
    python -m dancedeets.jobs.runner --job=start_spiders
"""

import json
import logging
import os
from typing import List

import scrapinghub

from dancedeets import keys
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics

logger = logging.getLogger(__name__)

# Spiders that are currently disabled
DISABLED_SPIDERS = ['EXPG', 'Boogiezone', 'IDA', 'mL', 'NeighborhoodStudio']


def get_spiders() -> List[str]:
    """Get list of active spiders."""
    all_spiders = [
        # NY
        'PMT',
        'Evolution',
        'Peridance',
        'BDC',
        'EXPG',
        # LA
        'Millenium',
        'EDGE',
        'DebbieReynolds',
        'TheLab',
        'Boogiezone',
        'IDA',
        'mL',
        'NeighborhoodStudio',
    ]
    return [s for s in all_spiders if s not in DISABLED_SPIDERS]


def get_shub_project():
    """Get ScrapingHub project connection."""
    api_key = keys.get('scrapinghub_key')
    conn = scrapinghub.Connection(api_key)
    project = scrapinghub.Project(conn, 27474)
    return project


def start_spiders(spiders: List[str], dry_run: bool = False) -> List[str]:
    """
    Start spider jobs on ScrapingHub.

    Args:
        spiders: List of spider names to run
        dry_run: If True, don't actually start spiders

    Returns:
        List of job keys for started spiders
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would start {len(spiders)} spiders: {spiders}")
        return [f"dry-run-{s}" for s in spiders]

    project = get_shub_project()
    job_keys = []

    for spider in spiders:
        try:
            job_id = project.schedule(spider)
            job_keys.append(job_id)
            logger.info(f"Scheduled spider {spider}: {job_id}")
        except Exception as e:
            logger.error(f"Error scheduling spider {spider}: {e}")

    logger.info(f"Scheduled {len(job_keys)} jobs: {job_keys}")
    return job_keys


def main(dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the start_spiders job.

    Args:
        dry_run: If True, don't actually start spiders

    Outputs:
        Writes job keys to stdout for workflow consumption
    """
    logger.info("Starting start_spiders job")

    metrics = JobMetrics()
    set_current_metrics(metrics)

    spiders = get_spiders()
    logger.info(f"Active spiders: {spiders}")

    job_keys = start_spiders(spiders, dry_run=dry_run)

    metrics.increment('spiders_started', len(job_keys))
    metrics.log_summary()

    # Output job keys for workflow to consume
    output = {
        'jobKeys': job_keys,
        'spidersStarted': len(job_keys),
    }
    print(json.dumps(output))


if __name__ == '__main__':
    main()
