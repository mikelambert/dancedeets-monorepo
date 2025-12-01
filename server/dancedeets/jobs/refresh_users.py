"""
Cloud Run Job: Refresh user profiles from Facebook.

Migrated from: dancedeets/users/user_tasks.py

This job refreshes user profile information from the Facebook API
and updates the local user records.

Usage:
    python -m dancedeets.jobs.runner --job=refresh_users
    python -m dancedeets.jobs.runner --job=refresh_users --all_users=true
"""

import logging
from typing import Optional

from dancedeets import fb_api
from dancedeets.jobs.base import Job, JobRunner
from dancedeets.jobs.fb_utils import FBJobContext, get_fblookup_params, get_multiple_tokens
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.mail import mailchimp_api

logger = logging.getLogger(__name__)


class RefreshUsersJob(Job):
    """
    Job that refreshes user profiles from Facebook.

    For each user:
    1. Check if they have a valid access token
    2. Fetch updated profile info from Facebook
    3. Update local user record
    4. Optionally update Mailchimp subscription
    """

    def __init__(
        self,
        fb_context: Optional[FBJobContext] = None,
        mailchimp_list_id: Optional[str] = None,
        dry_run: bool = False,
    ):
        super().__init__()
        self.fb_context = fb_context
        self.mailchimp_list_id = mailchimp_list_id or mailchimp_api.get_list_id()
        self.dry_run = dry_run
        logger.info(f"RefreshUsersJob initialized, mailchimp_list_id={mailchimp_list_id}")

    def run(self, user) -> None:
        """Process a single user."""
        if user.expired_oauth_token:
            logger.info(
                f"Skipping user {user.fb_uid} ({user.full_name}) "
                "due to expired access_token"
            )
            self.metrics.increment('users_skipped_expired')
            if not self.dry_run:
                user.put()  # Save any pending changes
            return

        # Get access token (prefer user's own token, fall back to context)
        access_token = user.fb_access_token
        if not access_token and self.fb_context:
            access_token = self.fb_context.access_token

        if not access_token:
            logger.info(
                f"Skipping user {user.fb_uid} ({user.full_name}) "
                "due to not having an access_token"
            )
            self.metrics.increment('users_skipped_no_token')
            if not self.dry_run:
                user.put()
            return

        # Fetch and update user from Facebook
        try:
            self._fetch_and_save_fb_user(user, access_token)
            self.metrics.increment('users_refreshed')
        except Exception as e:
            logger.error(f"Error refreshing user {user.fb_uid}: {e}")
            self.metrics.increment('users_failed')

    def _fetch_and_save_fb_user(self, user, access_token: str) -> None:
        """Fetch user data from Facebook and save."""
        fbl = fb_api.FBLookup(user.fb_uid, access_token)

        if self.fb_context:
            fbl.allow_cache = self.fb_context.allow_cache
            if self.fb_context.oldest_allowed:
                fbl.db.oldest_allowed = self.fb_context.oldest_allowed

        try:
            fb_user = fbl.get(fb_api.LookupUser, user.fb_uid)
        except fb_api.ExpiredOAuthToken as e:
            logger.info(f"Auth token now expired for {user.fb_uid}: {e}")
            user.expired_oauth_token_reason = str(e.args[0]) if e.args else "Unknown"
            user.expired_oauth_token = True
            if not self.dry_run:
                user.put()
            self.metrics.increment('users_token_expired')
            return

        if self.dry_run:
            logger.info(f"[DRY RUN] Would update user {user.fb_uid}")
            return

        user.compute_derived_properties(fb_user)
        user.put()

        # Update Mailchimp if configured
        # Note: mailchimp update is typically handled by user.put() via signals


def main(
    all_users: bool = False,
    dry_run: bool = False,
    **kwargs,
) -> None:
    """
    Main entry point for the refresh_users job.

    Args:
        all_users: If True, include users with expired tokens
        dry_run: If True, don't save changes
    """
    logger.info(f"Starting refresh_users job, all_users={all_users}")

    # Get tokens for Facebook API access
    try:
        tokens = get_multiple_tokens(token_count=50)
        logger.info(f"Got {len(tokens)} access tokens for rotation")
    except Exception as e:
        logger.warning(f"Could not get multiple tokens: {e}")
        tokens = []

    # Create FB context with token pool
    fb_context = FBJobContext(
        fb_uid='system',  # System-level access
        access_tokens=tokens,
        allow_cache=True,
    ) if tokens else None

    # Get Mailchimp list ID
    try:
        mailchimp_list_id = mailchimp_api.get_list_id()
    except Exception as e:
        logger.warning(f"Could not get Mailchimp list ID: {e}")
        mailchimp_list_id = None

    job = RefreshUsersJob(
        fb_context=fb_context,
        mailchimp_list_id=mailchimp_list_id,
        dry_run=dry_run,
    )
    set_current_metrics(job.metrics)

    runner = JobRunner(job)

    # Build filters
    filters = []
    if not all_users:
        filters.append(('expired_oauth_token', '=', False))

    runner.run_from_datastore(
        entity_kind='dancedeets.users.users.User',
        filters=filters,
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
