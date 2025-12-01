# Cloud Run Jobs framework for DanceDeets
# Replaces legacy App Engine MapReduce/Pipeline

from .base import Job, JobRunner, BatchJob
from .fb_utils import get_fblookup, get_fblookup_params, get_multiple_tokens, FBJobContext
from .metrics import JobMetrics, GroupedMetrics
from .gcs_output import GCSOutputWriter

__all__ = [
    # Base classes
    'Job',
    'JobRunner',
    'BatchJob',
    # Facebook utilities
    'FBJobContext',
    'get_fblookup',
    'get_fblookup_params',
    'get_multiple_tokens',
    # Metrics
    'JobMetrics',
    'GroupedMetrics',
    # GCS output
    'GCSOutputWriter',
]

# Available jobs (for reference):
#
# Phase 2 - Simple mapper jobs:
#   - notify_users: Send push notifications by timezone
#   - post_japan_events: Post Japan events to social media
#   - compute_rankings: Compute city/country rankings
#   - compute_user_stats: Compute user event statistics
#   - refresh_users: Refresh user profiles from Facebook
#   - send_weekly_emails: Send weekly event digest emails
#
# Phase 3 - GCS output jobs:
#   - generate_sitemaps: Generate XML sitemaps
#   - dump_potential_events: Export potential events to CSV
#   - generate_training_data: Generate ML training data
#   - classify_events_ml: ML event classification
#   - auto_add_events: Auto-add dance events
#
# Phase 4 - MapReduce pipeline replacements:
#   - count_unique_attendees: Count unique RSVPs by city
#   - update_source_stats: Update source quality metrics
#   - scrape_and_classify: Scrape sources and classify events
#
# Phase 5 - Pipeline orchestration (Cloud Workflows):
#   - start_spiders: Start ScrapingHub spider jobs
#   - reindex_classes: Rebuild class search index
#   - email_crawl_errors: Send crawl error reports
