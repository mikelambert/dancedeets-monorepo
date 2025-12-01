"""
Cloud Run Job runner entry point.

This module provides a CLI interface for running jobs from Cloud Run.
Jobs are specified by name and executed with the provided parameters.

Usage:
    python -m dancedeets.jobs.runner --job=notify_users --offset=8
    python -m dancedeets.jobs.runner --job=generate_sitemaps --vertical=STREET
"""

import argparse
import importlib
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Registry of available jobs
JOB_REGISTRY = {
    # Phase 2: Simple mapper jobs
    'notify_users': 'dancedeets.jobs.notify_users',
    'post_japan_events': 'dancedeets.jobs.post_japan_events',
    'compute_rankings': 'dancedeets.jobs.compute_rankings',
    'compute_user_stats': 'dancedeets.jobs.compute_user_stats',
    'refresh_users': 'dancedeets.jobs.refresh_users',
    'send_weekly_emails': 'dancedeets.jobs.send_weekly_emails',

    # Phase 3: GCS output jobs
    'generate_sitemaps': 'dancedeets.jobs.generate_sitemaps',
    'dump_potential_events': 'dancedeets.jobs.dump_potential_events',
    'generate_training_data': 'dancedeets.jobs.generate_training_data',
    'classify_events_ml': 'dancedeets.jobs.classify_events_ml',
    'auto_add_events': 'dancedeets.jobs.auto_add_events',

    # Phase 4: MapReduce pipeline jobs
    'count_unique_attendees': 'dancedeets.jobs.count_unique_attendees',
    'update_source_stats': 'dancedeets.jobs.update_source_stats',
    'scrape_and_classify': 'dancedeets.jobs.scrape_and_classify',
    'find_access_tokens': 'dancedeets.jobs.find_access_tokens',

    # Phase 5: Pipeline orchestration jobs (individual steps)
    'start_spiders': 'dancedeets.jobs.start_spiders',
    'reindex_classes': 'dancedeets.jobs.reindex_classes',
    'email_crawl_errors': 'dancedeets.jobs.email_crawl_errors',
}


def run_job(job_name: str, **kwargs) -> None:
    """
    Run a job by name with the given parameters.

    Args:
        job_name: Name of the job from JOB_REGISTRY
        **kwargs: Job-specific parameters
    """
    if job_name not in JOB_REGISTRY:
        available = ', '.join(sorted(JOB_REGISTRY.keys()))
        raise ValueError(f"Unknown job: {job_name}. Available jobs: {available}")

    module_path = JOB_REGISTRY[job_name]
    logger.info(f"Loading job module: {module_path}")

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        logger.error(f"Failed to import job module {module_path}: {e}")
        raise

    if not hasattr(module, 'main'):
        raise ValueError(f"Job module {module_path} must have a main() function")

    logger.info(f"Running job: {job_name}")
    logger.info(f"Parameters: {kwargs}")

    # Cloud Run Job environment info
    task_index = os.environ.get('CLOUD_RUN_TASK_INDEX', '0')
    task_count = os.environ.get('CLOUD_RUN_TASK_COUNT', '1')
    logger.info(f"Task {int(task_index) + 1} of {task_count}")

    try:
        module.main(**kwargs)
        logger.info(f"Job {job_name} completed successfully")
    except Exception as e:
        logger.error(f"Job {job_name} failed: {e}")
        raise


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run a DanceDeets batch job')
    parser.add_argument(
        '--job',
        required=True,
        help='Name of the job to run',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no side effects)',
    )

    # Allow arbitrary additional arguments
    args, unknown = parser.parse_known_args()

    # Parse unknown args as key=value pairs
    extra_args = {}
    for arg in unknown:
        if '=' in arg:
            key, value = arg.split('=', 1)
            key = key.lstrip('-')
            # Try to convert to appropriate types
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
            extra_args[key] = value

    return args, extra_args


def main():
    """Main entry point for the job runner."""
    args, extra_args = parse_args()

    if args.dry_run:
        extra_args['dry_run'] = True

    run_job(args.job, **extra_args)


if __name__ == '__main__':
    main()
