import datetime
import logging

import gcm

import keys

EVENT_REMINDER = 'EVENT_REMINDER'
EVENT_ADDED = 'EVENT_ADDED'

def _get_duration_seconds(event):
    start_time = event.start_time
    end_notify_window = event.end_time or event.start_time
    now = datetime.datetime.now(start_time.tzinfo)
    duration = (end_notify_window - now)
    max_duration = 4 * 7 * 24 * 60 * 60 # 4 weeks
    duration_seconds = duration.seconds + duration.days * 24 * 60 * 60
    duration_seconds = min(duration_seconds, max_duration)
    return duration_seconds

def rsvp_notify(user, event):
    duration_seconds = _get_duration_seconds(event)
    extra_data = {
        'notification_type': EVENT_REMINDER,

        # Deliver the message immediately
        'delay_while_idle': 0,

        # Keep trying to deliver it, as long as the event is scheduled
        # If the phone doesn't come online until after the event is completed, ignore it.
        'time_to_live': duration_seconds,
    }
    return real_notify(user, event.id, extra_data)

def add_notify(user, event_id):
    extra_data = {
        'notification_type': EVENT_ADDED,
    }
    return real_notify(user, event_id, extra_data)

def can_notify(user):
    tokens = user.device_tokens('android')
    return bool(tokens)

def real_notify(user, event_id, extra_data):
    if not can_notify(user):
        logging.info("No android GCM tokens.")
        return

    # We don't pass debug=True, because gcm.py library keeps adding more loggers ad-infinitum.
    # Instead we call GCM.enable_logging() once at the top-level.
    g = gcm.GCM(keys.get('google_server_key'))
    tokens = user.device_tokens('android')

    data = {
        # Important data for clientside lookups
        'event_id': event_id,
    }
    data.update(extra_data)
    response = g.json_request(registration_ids=tokens, data=data)

    changed_tokens = False
    if 'errors' in response:
        for error, reg_ids in response['errors'].iteritems():
            if error in ('NotRegistered', 'InvalidRegistration'):
                for reg_id in reg_ids:
                    tokens.remove(reg_id)
                    changed_tokens = True
            else:
                logging.error("Error for user %s with event %s: %s", user.fb_uid, event_id, error)

    if 'canonical' in response:
        for reg_id, canonical_id in response['canonical'].iteritems():
            tokens.remove(reg_id)
            tokens.append(canonical_id)
            changed_tokens = True

    if changed_tokens:
        user.put()

    logging.info("User %s (%s), event %s: sent notification!", user.fb_uid, user.full_name, event_id)

    return 'success' in response

