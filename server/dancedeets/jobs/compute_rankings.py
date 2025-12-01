"""
Cloud Run Job: Compute city/country rankings by events and users.

Migrated from: dancedeets/rankings/rankings.py

This job counts events and users by city/country for ranking calculations.
Results are stored in memcache for display on the website.

Usage:
    python -m dancedeets.jobs.runner --job=compute_rankings --ranking_type=events --vertical=STREET
    python -m dancedeets.jobs.runner --job=compute_rankings --ranking_type=users
"""

import datetime
import logging

from dancedeets.jobs.base import Job, JobRunner
from dancedeets.jobs.metrics import GroupedMetrics, JobMetrics, set_current_metrics
from dancedeets.rankings import rankings
from dancedeets.util import memcache

logger = logging.getLogger(__name__)

# Time period definitions (from rankings.py)
LAST_WEEK = "LAST_WEEK"
LAST_MONTH = "LAST_MONTH"
ALL_TIME = "ALL_TIME"


def get_time_periods(timestamp):
    """Get applicable time periods for a given timestamp."""
    now = datetime.datetime.now()
    if timestamp > now - datetime.timedelta(days=7):
        yield LAST_WEEK
    if timestamp > now - datetime.timedelta(days=31):
        yield LAST_MONTH
    yield ALL_TIME


class ComputeEventRankingsJob(Job):
    """
    Job that counts events by city for rankings.

    Iterates over all events (optionally filtered by vertical) and
    counts them by city and country for different time periods.
    """

    def __init__(self, vertical: str = None, dry_run: bool = False):
        super().__init__()
        self.vertical = vertical
        self.dry_run = dry_run
        self.city_counts = GroupedMetrics()
        self.country_counts = GroupedMetrics()
        logger.info(f"ComputeEventRankingsJob initialized for vertical={vertical}")

    def run(self, dbevent) -> None:
        """Process a single event."""
        if not dbevent.start_time:  # deleted event, don't count
            self.metrics.increment('events_skipped_deleted')
            return

        if not dbevent.latitude or not dbevent.longitude:
            self.metrics.increment('events_skipped_no_location')
            return

        city = dbevent.city_name
        country = dbevent.country

        # Determine which time periods this event counts for
        timestamp = dbevent.creation_time or dbevent.start_time
        for time_period in get_time_periods(timestamp):
            if city:
                self.city_counts.increment(city, time_period)
            if country:
                self.country_counts.increment(country, time_period)

        self.metrics.increment('events_processed')

    def teardown(self) -> None:
        """Save rankings to memcache after processing."""
        if self.dry_run:
            logger.info("[DRY RUN] Would save rankings to memcache")
            logger.info(f"City counts: {len(self.city_counts.get_all_groups())} cities")
            logger.info(f"Country counts: {len(self.country_counts.get_all_groups())} countries")
            return

        # Store city rankings
        city_rankings = {}
        for city, periods in self.city_counts.get_all_groups().items():
            city_rankings[city] = periods

        # Store country rankings
        country_rankings = {}
        for country, periods in self.country_counts.get_all_groups().items():
            country_rankings[country] = periods

        # Save to memcache (similar to _compute_summary)
        vertical_key = f":{self.vertical}" if self.vertical else ""
        memcache.set(
            f"CityEventRankings{vertical_key}",
            city_rankings,
            rankings.TOTALS_EXPIRY,
        )
        memcache.set(
            f"CountryEventRankings{vertical_key}",
            country_rankings,
            rankings.TOTALS_EXPIRY,
        )

        logger.info(f"Saved rankings for {len(city_rankings)} cities, {len(country_rankings)} countries")

        # Update the totals summary
        total_events = sum(
            periods.get(ALL_TIME, 0)
            for periods in city_rankings.values()
        )
        logger.info(f"Total events (all time): {total_events}")


class ComputeUserRankingsJob(Job):
    """
    Job that counts users by city for rankings.

    Iterates over all users and counts them by city for different time periods.
    """

    def __init__(self, dry_run: bool = False):
        super().__init__()
        self.dry_run = dry_run
        self.city_counts = GroupedMetrics()
        logger.info("ComputeUserRankingsJob initialized")

    def run(self, user) -> None:
        """Process a single user."""
        user_city = user.city_name
        if not user_city:
            self.metrics.increment('users_skipped_no_city')
            return

        timestamp = user.creation_time
        if not timestamp:
            # Use ALL_TIME if no creation time
            self.city_counts.increment(user_city, ALL_TIME)
        else:
            for time_period in get_time_periods(timestamp):
                self.city_counts.increment(user_city, time_period)

        self.metrics.increment('users_processed')

    def teardown(self) -> None:
        """Save rankings to memcache after processing."""
        if self.dry_run:
            logger.info("[DRY RUN] Would save user rankings to memcache")
            logger.info(f"City counts: {len(self.city_counts.get_all_groups())} cities")
            return

        # Store city rankings
        city_rankings = {}
        for city, periods in self.city_counts.get_all_groups().items():
            city_rankings[city] = periods

        memcache.set(
            "CityUserRankings",
            city_rankings,
            rankings.TOTALS_EXPIRY,
        )

        logger.info(f"Saved user rankings for {len(city_rankings)} cities")

        # Update the totals summary
        total_users = sum(
            periods.get(ALL_TIME, 0)
            for periods in city_rankings.values()
        )
        logger.info(f"Total users (all time): {total_users}")


def main(
    ranking_type: str = 'events',
    vertical: str = None,
    dry_run: bool = False,
    **kwargs,
) -> None:
    """
    Main entry point for the compute_rankings job.

    Args:
        ranking_type: 'events' or 'users'
        vertical: Optional vertical filter (e.g., 'STREET') for events
        dry_run: If True, don't save to memcache
    """
    logger.info(f"Starting compute_rankings job: type={ranking_type}, vertical={vertical}")

    if ranking_type == 'events':
        job = ComputeEventRankingsJob(vertical=vertical, dry_run=dry_run)
        entity_kind = 'dancedeets.events.eventdata.DBEvent'
        filters = []
        if vertical:
            filters.append(('verticals', '=', vertical))
    elif ranking_type == 'users':
        job = ComputeUserRankingsJob(dry_run=dry_run)
        entity_kind = 'dancedeets.users.users.User'
        filters = []
    else:
        raise ValueError(f"Unknown ranking_type: {ranking_type}")

    set_current_metrics(job.metrics)
    runner = JobRunner(job)

    runner.run_from_datastore(
        entity_kind=entity_kind,
        filters=filters,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
