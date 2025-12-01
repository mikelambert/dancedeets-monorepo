"""
Cloud Run Job: Send push notifications about new events to users.

Migrated from: dancedeets/notifications/added_events.py

This job runs hourly and sends notifications to users in a specific
timezone about recently added events near them.

Usage:
    python -m dancedeets.jobs.runner --job=notify_users --offset=8
    python -m dancedeets.jobs.runner --job=notify_users  # auto-calculates offset
"""

import datetime
import logging
import time

from google.cloud import datastore

from dancedeets.jobs.base import Job, JobRunner
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.loc import gmaps_api
from dancedeets.loc import math as loc_math
from dancedeets.notifications import android
from dancedeets.search import search
from dancedeets.search import search_base

logger = logging.getLogger(__name__)


def get_time_offset() -> float:
    """
    Calculate the timezone offset to target for 4pm local time notifications.

    Returns:
        Float timezone offset (e.g., 8.0 for UTC+8)
    """
    desired_hour = 16  # send new-event notifications at 4pm
    current_hour = datetime.datetime.now().hour  # should be UTC hour
    offset = desired_hour - current_hour
    if offset <= -12:
        offset += 24
    if offset > 12:
        offset -= 24
    return float(offset)


class NotifyUsersJob(Job):
    """
    Job that sends push notifications about new events to users.

    For each user in the target timezone:
    1. Check if they can receive Android notifications
    2. Search for events near their location added in the last 24 hours
    3. Send push notifications for each new event
    """

    def __init__(self, offset: float = None, dry_run: bool = False):
        super().__init__()
        self.offset = offset if offset is not None else get_time_offset()
        self.dry_run = dry_run
        logger.info(f"NotifyUsersJob initialized for timezone offset {self.offset}")

    def run(self, user) -> None:
        """Process a single user."""
        # Check if user can receive notifications
        if not android.can_notify(user):
            self.metrics.increment('users_skipped_no_android')
            return

        if not user:
            logger.error("No user provided")
            return

        if user.expired_oauth_token:
            logger.info(f"User has expired token, skipping: {user.fb_uid}")
            self.metrics.increment('users_skipped_expired_token')
            return

        user_location = user.location
        if not user_location:
            self.metrics.increment('users_skipped_no_location')
            return

        logger.info(f"Processing user {user.fb_uid}")

        distance_in_km = user.distance_in_km()
        min_attendees = user.min_attendees

        # Search for relevant events
        geocode = gmaps_api.lookup_address(user_location)
        if not geocode:
            self.metrics.increment('users_skipped_geocode_failed')
            return

        bounds = loc_math.expand_bounds(geocode.latlng_bounds(), distance_in_km)
        query = search_base.SearchQuery(
            time_period=search_base.TIME_UPCOMING,
            bounds=bounds,
            min_attendees=min_attendees,
        )

        one_day_ago = time.mktime(
            (datetime.datetime.now() - datetime.timedelta(hours=24)).timetuple()
        )

        search_query = search.Search(query)
        search_query.extra_fields = ['creation_time']
        search_results = search_query._get_candidate_doc_events()

        # Filter to recently added events
        recent_events = [
            x.doc_id
            for x in search_results
            if x.field('creation_time').value > one_day_ago
        ]

        logger.info(
            f"Found {len(search_results)} search results, "
            f"{len(recent_events)} new events for user {user.fb_uid}"
        )

        self.metrics.increment('events_found', len(recent_events))

        for event_id in recent_events:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would notify user {user.fb_uid} about event {event_id}")
                self.metrics.increment('notifications_would_send')
            else:
                if android.add_notify(user, event_id):
                    logger.info(f"Sent notification to {user.fb_uid} for event {event_id}")
                    self.metrics.increment('notifications_sent')

        self.metrics.increment('users_processed')


def main(offset: float = None, dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the notify_users job.

    Args:
        offset: Timezone offset to target (auto-calculated if not provided)
        dry_run: If True, don't actually send notifications
    """
    if offset is None:
        offset = get_time_offset()

    logger.info(f"Starting notify_users job for timezone offset {offset}")

    job = NotifyUsersJob(offset=offset, dry_run=dry_run)
    set_current_metrics(job.metrics)

    runner = JobRunner(job)

    # Query users in the target timezone range
    filters = [
        ('timezone_offset', '>=', offset),
        ('timezone_offset', '<', offset + 1),
    ]

    runner.run_from_datastore(
        entity_kind='dancedeets.users.users.User',
        filters=filters,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
