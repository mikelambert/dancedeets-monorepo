"""
Cloud Run Job: Compute user event statistics.

Migrated from: dancedeets/users/user_event_tasks.py

This job calculates statistics for each user about how many events
they've contributed (auto-added, hand-added, etc.).

Usage:
    python -m dancedeets.jobs.runner --job=compute_user_stats
"""

import logging

from dancedeets.jobs.base import Job, JobRunner
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.events import eventdata
from dancedeets.event_scraper import potential_events

logger = logging.getLogger(__name__)


def update_user_qualities(user) -> dict:
    """
    Calculate and update user event contribution statistics.

    Returns:
        Dict with the calculated statistics
    """
    # Query potential events where this user is a source
    # STR_ID_MIGRATE: using long() for fb_uid
    try:
        fb_uid_long = int(user.fb_uid)
    except (ValueError, TypeError):
        fb_uid_long = user.fb_uid

    source_potential_events = potential_events.PotentialEvent.gql(
        'WHERE source_ids = :graph_id',
        graph_id=fb_uid_long
    ).fetch(1000)

    # Get the actual events that were added
    added_events = eventdata.DBEvent.get_by_ids(
        [x.fb_event_id for x in source_potential_events]
    )

    # Count auto-added events
    num_auto_added = len([
        x for x in added_events
        if x and x.creating_method in [eventdata.CM_AUTO, eventdata.CM_AUTO_ATTENDEE]
    ])

    # Count auto-added events owned by this user
    num_auto_added_own = len([
        x for x in added_events
        if x and x.creating_method in [eventdata.CM_AUTO, eventdata.CM_AUTO_ATTENDEE]
        and x.owner_fb_uid == user.fb_uid
    ])

    # Count hand-added events (created by this user)
    # STR_ID_MIGRATE
    num_hand_added = len([
        x for x in added_events
        if x and x.creating_method == eventdata.CM_USER
        and str(x.creating_fb_uid) == user.fb_uid
    ])

    # Count hand-added events owned by this user
    # STR_ID_MIGRATE
    num_hand_added_own = len([
        x for x in added_events
        if x and x.creating_method == eventdata.CM_USER
        and str(x.creating_fb_uid) == user.fb_uid
        and x.owner_fb_uid == user.fb_uid
    ])

    # Update user properties
    user.num_auto_added_events = num_auto_added
    user.num_auto_added_own_events = num_auto_added_own
    user.num_hand_added_events = num_hand_added
    user.num_hand_added_own_events = num_hand_added_own

    return {
        'auto_added': num_auto_added,
        'auto_added_own': num_auto_added_own,
        'hand_added': num_hand_added,
        'hand_added_own': num_hand_added_own,
    }


class ComputeUserStatsJob(Job):
    """
    Job that computes event statistics for each user.

    For each user, counts:
    - Auto-added events (via ML classifier)
    - Hand-added events (manually added by user)
    - Events owned by the user
    """

    def __init__(self, dry_run: bool = False):
        super().__init__()
        self.dry_run = dry_run
        logger.info("ComputeUserStatsJob initialized")

    def run(self, user) -> None:
        """Process a single user."""
        try:
            stats = update_user_qualities(user)

            if self.dry_run:
                logger.info(
                    f"[DRY RUN] User {user.fb_uid}: "
                    f"auto={stats['auto_added']}, hand={stats['hand_added']}"
                )
                self.metrics.increment('users_would_update')
            else:
                user.put()
                self.metrics.increment('users_updated')

            # Track totals
            self.metrics.increment('total_auto_added', stats['auto_added'])
            self.metrics.increment('total_hand_added', stats['hand_added'])

        except Exception as e:
            logger.error(f"Error processing user {user.fb_uid}: {e}")
            self.metrics.increment('users_failed')


def main(dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the compute_user_stats job.

    Args:
        dry_run: If True, don't save changes to users
    """
    logger.info("Starting compute_user_stats job")

    job = ComputeUserStatsJob(dry_run=dry_run)
    set_current_metrics(job.metrics)

    runner = JobRunner(job)
    runner.run_from_datastore(
        entity_kind='dancedeets.users.users.User',
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
