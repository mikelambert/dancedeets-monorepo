"""
User event notifications.

The main batch processing has been migrated to Cloud Run Jobs.
See: dancedeets.jobs.notify_users

This module retains:
- promote_events_to_user(): Core notification logic (used by jobs and dev handler)
- /tasks/promote_new_events_to_user: Dev handler for testing single user
"""
import datetime
import logging
import time

from dancedeets import app
from dancedeets import base_servlet
from dancedeets.loc import gmaps_api
from dancedeets.loc import math
from dancedeets.search import search
from dancedeets.search import search_base
from dancedeets.users import users
from . import android


def get_time_offset():
    """Calculate timezone offset to target for 4pm local notifications."""
    desired_hour = 16  # send new-event notifications at 4pm
    current_hour = datetime.datetime.now().hour  # should be UTC hour
    offset = desired_hour - current_hour
    if offset <= -12:
        offset += 24
    if offset > 12:
        offset -= 24
    return float(offset)


# For development/testing only
@app.route('/tasks/promote_new_events_to_user')
class RemindUserHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        user_id = self.request.get('user_id')
        user = users.User.get_by_id(user_id)
        promote_events_to_user(user)


def promote_events_to_user(user):
    """
    Send push notifications about new events to a user.

    This is the core notification logic used by both:
    - Cloud Run Job: dancedeets.jobs.notify_users
    - Dev handler: /tasks/promote_new_events_to_user
    """
    # TODO: Adjust when we have iphone notifications
    if not android.can_notify(user):
        return

    logging.info("Promoting new events to user %s", user.fb_uid)
    user = users.User.get_by_id(user.fb_uid)
    if not user:
        logging.error("No user found: %s", user.fb_uid)
        return
    if user.expired_oauth_token:
        logging.info("User has expired token, aborting: %s", user.fb_uid)
        return

    user_location = user.location
    if not user_location:
        return
    distance_in_km = user.distance_in_km()
    min_attendees = user.min_attendees

    # search for relevant events
    geocode = gmaps_api.lookup_address(user_location)
    if not geocode:
        return None
    bounds = math.expand_bounds(geocode.latlng_bounds(), distance_in_km)
    query = search_base.SearchQuery(
        time_period=search_base.TIME_UPCOMING,
        bounds=bounds,
        min_attendees=min_attendees
    )

    one_day_ago = time.mktime(
        (datetime.datetime.now() - datetime.timedelta(hours=24)).timetuple()
    )

    search_query = search.Search(query)
    search_query.extra_fields = ['creation_time']
    search_results = search_query._get_candidate_doc_events()
    # TODO: can we move this filter into the search query itself??
    recent_events = [
        x.doc_id for x in search_results
        if x.field('creation_time').value > one_day_ago
    ]

    logging.info(
        "Found %s search_results, %s new events",
        len(search_results), len(recent_events)
    )
    for event_id in recent_events:
        if android.add_notify(user, event_id):
            logging.info("Sent notification!")
    # TODO: iphone_notify!
