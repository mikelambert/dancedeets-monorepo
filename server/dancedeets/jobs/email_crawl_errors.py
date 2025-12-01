"""
Cloud Run Job: Email crawl errors from spider jobs.

Migrated from: dancedeets/classes/class_pipeline.py (EmailErrors)

This job collects errors from completed spider jobs and sends
an email report.

Usage:
    python -m dancedeets.jobs.runner --job=email_crawl_errors --job_keys=key1,key2
"""

import datetime
import json
import logging
import os
from typing import Dict, List

import scrapinghub

from dancedeets import keys
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.mail import mandrill_api

logger = logging.getLogger(__name__)


def get_shub_project():
    """Get ScrapingHub project connection."""
    api_key = keys.get('scrapinghub_key')
    conn = scrapinghub.Connection(api_key)
    project = scrapinghub.Project(conn, 27474)
    return project


def collect_errors(job_keys: List[str]) -> Dict[str, List[str]]:
    """
    Collect errors from completed spider jobs.

    Args:
        job_keys: List of ScrapingHub job keys

    Returns:
        Dict mapping spider name to list of error messages
    """
    project = get_shub_project()
    error_lines: Dict[str, List[str]] = {}

    for job_key in job_keys:
        try:
            job = project.job(job_key)
            spider_name = job.info.get('spider', job_key)

            # Check for no items scraped
            if not job.info.get('items_scraped'):
                error_lines.setdefault(spider_name, []).append(
                    'Could not find any items.'
                )

            # Collect error-level log entries
            for line in job.log():
                if line.get('level', 0) >= 40:  # ERROR level
                    error_lines.setdefault(spider_name, []).append(
                        line.get('message', str(line))
                    )

        except Exception as e:
            logger.error(f"Error collecting logs for {job_key}: {e}")
            error_lines.setdefault(job_key, []).append(f"Error collecting logs: {e}")

    return error_lines


def send_error_email(
    error_lines: Dict[str, List[str]],
    run_time: datetime.datetime,
    dry_run: bool = False,
) -> None:
    """
    Send email report of crawl errors.

    Args:
        error_lines: Dict mapping spider name to error messages
        run_time: When the crawl started
        dry_run: If True, don't actually send email
    """
    if not error_lines:
        logger.info("No errors to report")
        return

    # Build email body
    rendered = ["The following crawl errors occurred:"]
    for crawler, errors in sorted(error_lines.items()):
        rendered.append(f"\n{crawler}:")
        rendered.extend(f"  - {error}" for error in errors)

    body = '\n'.join(rendered)
    logger.warning(body)

    if dry_run:
        logger.info("[DRY RUN] Would send error email")
        return

    subject = f"Crawl Errors for {run_time.strftime('%b %d, %Y: %H:%M')}"
    message = {
        'from_email': 'reports@dancedeets.com',
        'from_name': 'DanceDeets Reports',
        'subject': subject,
        'to': [{
            'email': 'reports@dancedeets.com',
            'name': 'DanceDeets Reports',
            'type': 'to',
        }],
        'text': body,
    }

    try:
        mandrill_api.send_message(message)
        logger.info("Error report email sent")
    except Exception as e:
        logger.error(f"Error sending email: {e}")


def main(
    job_keys: str = None,
    run_time: str = None,
    dry_run: bool = False,
    **kwargs,
) -> None:
    """
    Main entry point for the email_crawl_errors job.

    Args:
        job_keys: Comma-separated list of ScrapingHub job keys
        run_time: ISO format timestamp of when crawl started
        dry_run: If True, don't send email
    """
    logger.info("Starting email_crawl_errors job")

    metrics = JobMetrics()
    set_current_metrics(metrics)

    # Parse job keys
    if not job_keys:
        logger.warning("No job_keys provided")
        return

    if isinstance(job_keys, str):
        keys_list = [k.strip() for k in job_keys.split(',') if k.strip()]
    else:
        keys_list = job_keys

    logger.info(f"Checking {len(keys_list)} jobs for errors")

    # Parse run time
    if run_time:
        try:
            crawl_time = datetime.datetime.fromisoformat(run_time)
        except ValueError:
            crawl_time = datetime.datetime.now()
    else:
        crawl_time = datetime.datetime.now()

    # Collect and send errors
    error_lines = collect_errors(keys_list)
    metrics.increment('spiders_checked', len(keys_list))
    metrics.increment('spiders_with_errors', len(error_lines))

    send_error_email(error_lines, crawl_time, dry_run=dry_run)

    metrics.log_summary()


if __name__ == '__main__':
    main()
