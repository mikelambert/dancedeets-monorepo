"""
User event statistics utilities.

The batch processing has been migrated to Cloud Run Jobs.
See: dancedeets.jobs.compute_user_stats

This module retains the core update_user_qualities function for reuse.
"""
from dancedeets.events import eventdata
from dancedeets.event_scraper import potential_events


def update_user_qualities(user):
    """
    Calculate and update user event contribution statistics.

    Counts:
    - Auto-added events (via ML classifier)
    - Auto-added own events (user is the event owner)
    - Hand-added events (manually added by user)
    - Hand-added own events (user is both creator and owner)
    """
    # STR_ID_MIGRATE
    try:
        fb_uid_long = int(user.fb_uid)
    except (ValueError, TypeError):
        fb_uid_long = user.fb_uid

    source_potential_events = potential_events.PotentialEvent.gql(
        'WHERE source_ids = :graph_id', graph_id=fb_uid_long
    ).fetch(1000)

    added_events = eventdata.DBEvent.get_by_ids(
        [x.fb_event_id for x in source_potential_events]
    )

    user.num_auto_added_events = len([
        x for x in added_events
        if x and x.creating_method in [eventdata.CM_AUTO, eventdata.CM_AUTO_ATTENDEE]
    ])
    user.num_auto_added_own_events = len([
        x for x in added_events
        if x and x.creating_method in [eventdata.CM_AUTO, eventdata.CM_AUTO_ATTENDEE]
        and x.owner_fb_uid == user.fb_uid
    ])
    # STR_ID_MIGRATE
    user.num_hand_added_events = len([
        x for x in added_events
        if x and x.creating_method == eventdata.CM_USER
        and str(x.creating_fb_uid) == user.fb_uid
    ])
    # STR_ID_MIGRATE
    user.num_hand_added_own_events = len([
        x for x in added_events
        if x and x.creating_method == eventdata.CM_USER
        and str(x.creating_fb_uid) == user.fb_uid
        and x.owner_fb_uid == user.fb_uid
    ])
