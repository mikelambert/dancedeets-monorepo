import datetime
from dateutil import parser
import logging

import gcm

import keys
from util import urls

EVENT_REMINDER = 'EVENT_REMINDER'
#TODO: start sending out these notifications too
EVENT_ADDED = 'EVENT_ADDED'

def _get_duration_seconds(event):
    start_time = parser.parse(event.fb_event['info'].get('start_time'))
    if 'end_time' in event.fb_event['info']:
        end_notify_window = parser.parse(event.fb_event['info'].get('end_time'))
    else:
        end_notify_window = start_time
    now = datetime.datetime.now(start_time.tzinfo)
    duration = (end_notify_window - now)
    max_duration = 4 * 7 * 24 * 60 * 60 # 4 weeks
    duration_seconds = duration.seconds + duration.days * 24 * 60 * 60
    duration_seconds = min(duration_seconds, max_duration)
    return duration_seconds

def notify(user, event):
    # TODO: We don't want to send raw URLs, or it pops open a "open with" dialog. Pass in a custom schema instead!
    url = urls.fb_event_url(event.fb_event_id)

    g = gcm.GCM(keys.get('google_server_key'), debug=True)
    tokens = user.device_tokens('android')
    if not tokens:
        logging.info("No android GCM tokens.")
        return

    duration_seconds = _get_duration_seconds(event)
    # for image stuff, we want to set subtext as required (with text optional)
    # for regular styles, both are optional (and we probably want text)
    data = {
        'notification_type': EVENT_REMINDER,

        # Important data for clientside lookups
        'event_id': event.fb_event_id,

        # Deliver the message immediately
        'delay_while_idle': 0,
        # Keep trying to deliver it, as long as the event is scheduled
        # If the phone doesn't come online until after the event is completed, ignore it.
        'time_to_live': duration_seconds,
    }
    # TODO: what happens if we send multiple notifications. last-one wins? Can we do a better job of prioritizing and aggregating these?
    response = g.json_request(registration_ids=tokens, data=data)

    changed_tokens = False
    if 'errors' in response:
        for error, reg_ids in response['errors'].iteritems():
            if error in ('NotRegistered', 'InvalidRegistration'):
                for reg_id in reg_ids:
                    tokens.remove(reg_id)
                    changed_tokens = True
            else:
                logging.error("Error for user %s with url %s: %s", user.fb_uid, url, error)

    if 'canonical' in response:
        for reg_id, canonical_id in response['canonical'].iteritems():
            tokens.remove(reg_id)
            tokens.append(canonical_id)
            changed_tokens = True

    if changed_tokens:
        user.put()

    return 'success' in response

