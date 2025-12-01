"""
Cloud Run Job: Send weekly event digest emails to users.

Migrated from: dancedeets/search/email_events.py

This job sends a weekly email to users with dance events near them.

Usage:
    python -m dancedeets.jobs.runner --job=send_weekly_emails
    python -m dancedeets.jobs.runner --job=send_weekly_emails --dry_run=true
"""

import datetime
import logging
import random
import re
import urllib.parse
from typing import Optional

from dancedeets import fb_api
from dancedeets import render_server
from dancedeets.jobs.base import Job, JobRunner
from dancedeets.jobs.fb_utils import FBJobContext, get_multiple_tokens
from dancedeets.jobs.metrics import JobMetrics, set_current_metrics
from dancedeets.loc import names
from dancedeets.logic import api_format
from dancedeets.logic import mobile
from dancedeets.mail import mandrill_api
from dancedeets.search import search_base
from dancedeets.search import search
from dancedeets.users import users

logger = logging.getLogger(__name__)


class NoEmailException(Exception):
    """Raised when email cannot be sent for a user."""
    pass


def email_for_user(user, fbl, should_send: bool = True):
    """
    Generate and optionally send a weekly email for a user.

    Args:
        user: User object
        fbl: FBLookup instance
        should_send: Whether to actually send the email

    Returns:
        The email message dict

    Raises:
        NoEmailException: If email cannot be sent for various reasons
    """
    if not user.send_email:
        raise NoEmailException('User has send_email==False')

    email_address = user.email
    if not email_address:
        raise NoEmailException('User does not have an email')

    # Check if we sent an email recently
    if user.weekly_email_send_date:
        if user.weekly_email_send_date > datetime.datetime.now() - datetime.timedelta(days=3):
            message = f"Skipping user {user.fb_uid} ({user.full_name}) because last weekly email was sent on {user.weekly_email_send_date}"
            logger.warning(message)
            raise NoEmailException(message)

    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)
    if 'profile' not in fb_user:
        raise NoEmailException(f'Could not find LookupUser: {fb_user}')

    user_location = user.location
    if not user_location:
        raise NoEmailException('User does not have location')

    # Build search query for this week's events
    d = datetime.date.today()
    start_time = d - datetime.timedelta(days=d.weekday())  # round down to last monday
    end_time = start_time + datetime.timedelta(days=8)
    data = {
        'location': user_location,
        'distance': user.distance_in_km(),
        'distance_units': 'km',
        'start': start_time,
        'end': end_time,
    }
    form = search_base.SearchForm(data=data)

    geocode = None
    distance = None
    if form.location.data:
        try:
            geocode, distance = search_base.get_geocode_with_distance(form)
        except Exception as e:
            raise NoEmailException(f'Could not normalize user location: {data}: {e}')

    try:
        search_query = form.build_query(start_end_query=True)
    except Exception:
        logger.error(f'Error looking up user location for user {user.fb_uid}, form: {form}')
        raise

    search_results = search.Search(search_query).get_search_results()
    if not search_results:
        raise NoEmailException('No search results for user')

    # Build the email content
    need_full_event = False
    json_search_response = api_format.build_search_results_api(
        form, search_query, search_results, (2, 0), need_full_event, geocode, distance, skip_people=True
    )
    locale = user.locale or 'en_US'
    email_unsubscribe_url = f'https://www.dancedeets.com/user/unsubscribe?email={urllib.parse.quote(email_address)}'
    props = {
        'user': {
            'userName': user.first_name or user.full_name or '',
            'city': user.city_name,
            'countryName': names.get_country_name(user.location_country),
        },
        'response': json_search_response,
        'currentLocale': locale.replace('_', '-'),
        'mobileIosUrl': mobile.IOS_URL,
        'mobileAndroidUrl': mobile.ANDROID_URL,
        'emailPreferencesUrl': email_unsubscribe_url,
    }

    # Render the email template
    email_template = 'weeklyMail.js'
    response = render_server.render_jsx(email_template, props, static_html=True)
    if response.error:
        message = f'Error rendering weeklyMail.js: {response.error}'
        logger.error(message)
        raise NoEmailException(message)

    mjml_response = render_server.render_mjml(response.markup)
    rendered_html = mjml_response['html']
    if mjml_response.get('errors'):
        message = f'Errors rendering weeklyMail.mjml: {mjml_response["errors"]}'
        logger.error(message)
        raise NoEmailException(message)

    # Build the message
    messages = [
        'Your Week in Dance: %s',
        'DanceDeets Weekly: %s',
        'Dance Events for %s',
    ]
    message_template = random.choice(messages)
    tag = re.sub(r'[^a-z]', '-', message_template.lower())[:50]
    tags = ['weekly', tag]

    subject = message_template % d.strftime('%b %d, %Y')
    message = {
        'from_email': 'events@dancedeets.com',
        'from_name': 'DanceDeets Events',
        'subject': subject,
        'to': [{
            'email': email_address,
            'name': user.full_name or user.first_name or '',
            'type': 'to',
        }],
        'html': rendered_html,
        'metadata': {
            'user_id': user.fb_uid,
            'email_type': 'weekly',
        },
        'tags': tags,
    }

    if should_send:
        logger.info(f'Sending weekly mail for user {user.fb_uid} ({user.full_name})')
        # Update the last-sent-time here, so any retryable errors don't cause emails to be multi-sent
        user = users.User.get_by_id(user.fb_uid)
        user.weekly_email_send_date = datetime.datetime.now()
        user.put()
        # And send the message now
        mandrill_api.send_message(message)

    return message


class SendWeeklyEmailsJob(Job):
    """
    Job that sends weekly event digest emails to users.

    For each user:
    1. Fetch user profile from Facebook
    2. Search for events near their location
    3. Render and send email via Mandrill
    """

    def __init__(
        self,
        fb_context: Optional[FBJobContext] = None,
        dry_run: bool = False,
    ):
        super().__init__()
        self.fb_context = fb_context
        self.dry_run = dry_run
        logger.info("SendWeeklyEmailsJob initialized")

    def run(self, user) -> None:
        """Process a single user."""
        # Get access token
        access_token = user.fb_access_token
        if not access_token and self.fb_context:
            access_token = self.fb_context.access_token

        if not access_token:
            logger.info(f"Skipping user {user.fb_uid} - no access token")
            self.metrics.increment('users_skipped_no_token')
            return

        # Create FBLookup for this user
        fbl = fb_api.FBLookup(user.fb_uid, access_token)
        if self.fb_context:
            fbl.allow_cache = self.fb_context.allow_cache

        # Fetch user data from Facebook
        fbl.request(fb_api.LookupUser, user.fb_uid)
        fbl.request(fb_api.LookupUserEvents, user.fb_uid)

        try:
            fbl.batch_fetch()
        except fb_api.ExpiredOAuthToken as e:
            logger.info(f"Auth token now expired for {user.fb_uid}: {e}")
            user.expired_oauth_token_reason = str(e.args[0]) if e.args else "Unknown"
            user.expired_oauth_token = True
            if not self.dry_run:
                user.put()
            self.metrics.increment('users_token_expired')
            return

        # Generate and send email
        try:
            should_send = not self.dry_run
            email_for_user(user, fbl, should_send=should_send)

            if self.dry_run:
                logger.info(f"[DRY RUN] Would send email to {user.fb_uid}")
                self.metrics.increment('emails_would_send')
            else:
                self.metrics.increment('emails_sent')

        except NoEmailException as e:
            logger.info(f"Not sending email for user {user.fb_uid}: {e}")
            self.metrics.increment('users_skipped_no_email')

        except Exception as e:
            logger.exception(f"Error sending email for user {user.fb_uid}")
            self.metrics.increment('emails_failed')


def main(dry_run: bool = False, **kwargs) -> None:
    """
    Main entry point for the send_weekly_emails job.

    Args:
        dry_run: If True, don't actually send emails
    """
    logger.info("Starting send_weekly_emails job")

    # Get tokens for Facebook API access
    try:
        tokens = get_multiple_tokens(token_count=50)
        logger.info(f"Got {len(tokens)} access tokens for rotation")
    except Exception as e:
        logger.warning(f"Could not get multiple tokens: {e}")
        tokens = []

    # Create FB context with token pool
    fb_context = FBJobContext(
        fb_uid='system',
        access_tokens=tokens,
        allow_cache=True,
    ) if tokens else None

    job = SendWeeklyEmailsJob(fb_context=fb_context, dry_run=dry_run)
    set_current_metrics(job.metrics)

    runner = JobRunner(job)
    runner.run_from_datastore(
        entity_kind='dancedeets.users.users.User',
    )

    job.metrics.log_summary()


if __name__ == '__main__':
    main()
