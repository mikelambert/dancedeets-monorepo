"""Android push notifications using Firebase Cloud Messaging (FCM).

This replaces the deprecated python-gcm library with firebase-admin.
"""

import datetime
import logging

import firebase_admin
from firebase_admin import credentials, messaging

from dancedeets import keys

# Notification types
EVENT_REMINDER = 'EVENT_REMINDER'
EVENT_ADDED = 'EVENT_ADDED'

# Initialize Firebase Admin SDK (only once)
_firebase_app = None


def _get_firebase_app():
    """Get or initialize the Firebase Admin app."""
    global _firebase_app
    if _firebase_app is None:
        # Initialize with default credentials or service account
        # In App Engine, this uses the default service account automatically
        try:
            _firebase_app = firebase_admin.get_app()
        except ValueError:
            # App not initialized yet
            cred = credentials.ApplicationDefault()
            _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def _get_duration_seconds(event):
    """Calculate the duration in seconds until event ends."""
    start_time = event.start_time
    end_notify_window = event.end_time or event.start_time
    now = datetime.datetime.now(start_time.tzinfo)
    duration = (end_notify_window - now)
    max_duration = 4 * 7 * 24 * 60 * 60  # 4 weeks
    duration_seconds = duration.seconds + duration.days * 24 * 60 * 60
    duration_seconds = min(duration_seconds, max_duration)
    return duration_seconds


def rsvp_notify(user, event):
    """Send RSVP reminder notification to user about an event."""
    duration_seconds = _get_duration_seconds(event)
    extra_data = {
        'notification_type': EVENT_REMINDER,
    }
    return real_notify(user, event.id, extra_data, ttl=duration_seconds)


def add_notify(user, event_id):
    """Send notification about a newly added event."""
    extra_data = {
        'notification_type': EVENT_ADDED,
    }
    return real_notify(user, event_id, extra_data)


def can_notify(user):
    """Check if user has Android device tokens."""
    tokens = user.device_tokens('android')
    return bool(tokens)


def real_notify(user, event_id, extra_data, ttl=None):
    """Send push notification to user's Android devices.

    Args:
        user: User object with device_tokens method
        event_id: ID of the event to notify about
        extra_data: Additional data to include in the notification
        ttl: Time-to-live in seconds (optional)

    Returns:
        True if notification was sent successfully, False otherwise
    """
    if not can_notify(user):
        logging.info("No android FCM tokens.")
        return False

    # Ensure Firebase is initialized
    _get_firebase_app()

    tokens = list(user.device_tokens('android'))

    # Build the data payload - all values must be strings
    data = {
        'event_id': str(event_id),
    }
    data.update({k: str(v) for k, v in extra_data.items()})

    # Build Android-specific config
    android_config = messaging.AndroidConfig(
        priority='normal',
        ttl=datetime.timedelta(seconds=ttl) if ttl else None,
    )

    # Track tokens that need to be updated
    tokens_to_remove = []
    success = False

    # Send to each token
    for token in tokens:
        message = messaging.Message(
            data=data,
            token=token,
            android=android_config,
        )

        try:
            response = messaging.send(message)
            logging.info("Successfully sent message: %s", response)
            success = True
        except messaging.UnregisteredError:
            # Token is no longer valid
            logging.info("Token %s is no longer registered, removing", token[:20])
            tokens_to_remove.append(token)
        except messaging.SenderIdMismatchError:
            # Token doesn't match our sender ID
            logging.warning("Token %s has sender ID mismatch, removing", token[:20])
            tokens_to_remove.append(token)
        except Exception as e:
            logging.error("Error sending to user %s for event %s: %s", user.fb_uid, event_id, str(e))

    # Update user's tokens if needed
    if tokens_to_remove:
        changed_tokens = False
        current_tokens = list(user.device_tokens('android'))
        for token in tokens_to_remove:
            if token in current_tokens:
                current_tokens.remove(token)
                changed_tokens = True
        if changed_tokens:
            user.put()

    if success:
        logging.info("User %s (%s), event %s: sent notification!", user.fb_uid, user.full_name, event_id)

    return success
