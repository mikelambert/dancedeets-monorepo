"""
Cloud Run Job: Generate XML sitemaps for search engine indexing.

Migrated from: dancedeets/sitemaps/events.py

This job generates XML sitemap files for all events and uploads them
to Google Cloud Storage for search engine crawlers.

Usage:
    python -m dancedeets.jobs.runner --job=generate_sitemaps
    python -m dancedeets.jobs.runner --job=generate_sitemaps --vertical=STREET --time_period=FUTURE
"""

import datetime
import logging
from typing import Optional

from lxml import etree

from dancedeets.jobs.base import BatchJob, JobRunner
from dancedeets.jobs.gcs_output import GCSOutputWriter, DEFAULT_BUCKET
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.util import urls

logger = logging.getLogger(__name__)


def generate_sitemap_entry(event) -> Optional[str]:
    """
    Generate a single sitemap XML entry for an event.

    Args:
        event: DBEvent instance

    Returns:
        XML string for the URL entry, or None if event should be skipped
    """
    if not event.has_content():
        return None

    url_node = etree.Element('url')

    # Location
    loc_node = etree.Element('loc')
    loc_node.text = urls.dd_event_url(event)
    url_node.append(loc_node)

    # Last modified (from Facebook updated_time)
    if event.is_fb_event:
        if 'updated_time' in event.fb_event.get('info', {}):
            lastmod_node = etree.Element('lastmod')
            updated = event.fb_event['info']['updated_time']
            updated = updated.replace('+0000', '+00:00')
            lastmod_node.text = updated
            url_node.append(lastmod_node)
        else:
            logger.debug(f'Event {event.id} does not have updated_time')

    # Calculate timing-based metadata
    if event.end_time:
        end_time = event.end_time
    else:
        end_time = event.start_time + datetime.timedelta(hours=2)

    start_time_delta = event.start_time - datetime.datetime.now()
    end_time_delta = end_time - datetime.datetime.now()
    event_delta = end_time - event.start_time

    # Change frequency and priority
    changefreq_node = etree.Element('changefreq')
    priority_node = etree.Element('priority')
    priority_node.text = '0.5'

    # Event is active and not a multi-week event
    if event_delta.days < 7 and start_time_delta.days <= 1 and end_time_delta.days >= 0:
        changefreq_node.text = 'hourly'
    # If it ended awhile ago
    elif end_time_delta.days < -30:
        changefreq_node.text = 'yearly'
        priority_node.text = '0.1'
    elif end_time_delta.days < -10:
        changefreq_node.text = 'weekly'
    # If it's coming up soon
    elif start_time_delta.days < 30:
        changefreq_node.text = 'daily'
    else:
        changefreq_node.text = 'weekly'

    url_node.append(changefreq_node)
    url_node.append(priority_node)

    # Return as single line
    return etree.tostring(url_node, encoding='unicode')


class GenerateSitemapsJob(BatchJob):
    """
    Job that generates XML sitemaps for events.

    Processes events in batches and writes sitemap entries to GCS.
    """

    def __init__(
        self,
        vertical: Optional[str] = None,
        time_period: Optional[str] = None,
        bucket_name: str = DEFAULT_BUCKET,
        dry_run: bool = False,
    ):
        super().__init__(batch_size=20)
        self.vertical = vertical
        self.time_period = time_period
        self.bucket_name = bucket_name
        self.dry_run = dry_run

        # Build output path
        parts = ['sitemaps']
        if vertical:
            parts.append(vertical.lower())
        if time_period:
            parts.append(time_period.lower())
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        parts.append(f'sitemap-{timestamp}.xml')
        self.blob_name = '/'.join(parts)

        self.output_writer = None
        logger.info(f"GenerateSitemapsJob initialized: vertical={vertical}, time_period={time_period}")

    def setup(self) -> None:
        """Initialize the output writer."""
        if not self.dry_run:
            self.output_writer = GCSOutputWriter(
                bucket_name=self.bucket_name,
                blob_name=self.blob_name,
                content_type='text/xml',
            )
            # Write XML header
            self.output_writer.write('<?xml version="1.0" encoding="UTF-8"?>')
            self.output_writer.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    def run_batch(self, events: list) -> None:
        """Process a batch of events."""
        for event in events:
            try:
                entry = generate_sitemap_entry(event)
                if entry:
                    if self.dry_run:
                        logger.debug(f"Would write sitemap entry for event {event.id}")
                        self.metrics.increment('entries_would_write')
                    else:
                        self.output_writer.write(entry)
                        self.metrics.increment('entries_written')
                else:
                    self.metrics.increment('events_skipped_no_content')
            except Exception as e:
                logger.error(f"Error generating sitemap for event {event.id}: {e}")
                self.metrics.increment('events_failed')

        self.metrics.increment('events_processed', len(events))

    def teardown(self) -> None:
        """Finalize and upload the sitemap."""
        if self.dry_run:
            logger.info("[DRY RUN] Would write sitemap to GCS")
            return

        if self.output_writer:
            # Write closing tag
            self.output_writer.write('</urlset>')
            uri = self.output_writer.flush()
            logger.info(f"Sitemap written to {uri}")


def main(
    vertical: Optional[str] = None,
    time_period: Optional[str] = None,
    bucket_name: str = DEFAULT_BUCKET,
    dry_run: bool = False,
    **kwargs,
) -> None:
    """
    Main entry point for the generate_sitemaps job.

    Args:
        vertical: Optional vertical filter (e.g., 'STREET')
        time_period: Optional time period filter (e.g., 'FUTURE', 'PAST')
        bucket_name: GCS bucket for output
        dry_run: If True, don't write to GCS
    """
    logger.info(f"Starting generate_sitemaps job: vertical={vertical}, time_period={time_period}")

    job = GenerateSitemapsJob(
        vertical=vertical,
        time_period=time_period,
        bucket_name=bucket_name,
        dry_run=dry_run,
    )
    set_current_metrics(job.metrics)

    runner = JobRunner(job)

    # Build filters
    filters = []
    if vertical:
        filters.append(('verticals', '=', vertical))
    if time_period:
        filters.append(('search_time_period', '=', time_period))

    runner.run_from_datastore_batched(
        entity_kind='dancedeets.events.eventdata.DBEvent',
        filters=filters,
        batch_size=20,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
