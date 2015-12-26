import datetime
from dateutil import parser
import logging
import urllib

from google.appengine.api import taskqueue

import app
import base_servlet
import fb_api
from events import eventdata
from users import users
from . import android

def setup_reminders(fb_uid, fb_user_events):
    event_results_json = fb_user_events['events']['data']
    event_ids = [x['id'] for x in event_results_json]
    existing_events = [x.string_id() for x in eventdata.DBEvent.get_by_ids(event_ids, keys_only=True) if x]
    logging.info("For user %s's %s events, %s are real dance events", fb_uid, len(event_ids), len(existing_events))
    for event in event_results_json:
        if event['id'] not in existing_events:
            continue
        logging.info("%s is dance event, checking dates..", event['id'])
        start_time = parser.parse(event['start_time'])
        # Otherwise it's at a specific time (we need the time with the timezone info included)
        # Also try to get it ten minutes before the Facebook event comes in, so that we aren't seen as the "dupe".
        start_notify_window = start_time - datetime.timedelta(hours=1, minutes=10)

        # I think 30 days is the limit for appengine tasks with ETA set, but it gets trickier with all the timezones.
        # And really, we run this code multiple times a day, so don't need to plan out more than a single day.
        # Otherwise if the user un-rsvp's for an event, we'll still have a zombie task waiting to notify them.
        # (And AppEngine doesn't like us removing-and-readding a named task item anyway)
        now = datetime.datetime.now(start_time.tzinfo)
        future_cutoff = now + datetime.timedelta(days=1)

        if 'end_time' in event:
            end_notify_window = parser.parse(event['end_time'])
        else:
            end_notify_window = start_time

        # Ignore events that started in the past
        if end_notify_window < now:
            continue
        # And ignore events that are too far in the future to care about yet
        if start_notify_window > future_cutoff:
            continue
        logging.info("For event %s, sending notifications at %s", event['id'], start_notify_window)
        try:
            taskqueue.add(
                method='GET',
                name='notify_user-%s-%s' % (fb_uid, event['id']),
                queue_name='mobile-notify-queue',
                eta=start_notify_window,
                url='/tasks/notify_user?'+urllib.urlencode(dict(
                    user_id=fb_uid,
                    event_id=event['id'])),
            )
        except (taskqueue.TaskAlreadyExistsError, taskqueue.TombstonedTaskError):
            pass

def _is_attending(user, event_id):
    fbl = user.get_fblookup()
    # For now, for simplicity, and because it's fast enough,
    # just load the user's entire events here via /user_id/events .
    # Instead of the targeted query via /event_id/attending/user_id .
    user_events = fbl.get(fb_api.LookupUserEvents, user.fb_uid, allow_cache=False)
    found_events = [x for x in user_events['events']['data'] if x['id'] == event_id]
    if not found_events:
        return False
    found_event = found_events[0]
    if found_event['rsvp_status'] != 'attending':
        return False
    return True

@app.route('/tasks/notify_user')
class NotifyUserHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        notify_user(self.request.get('user_id'), self.request.get('event_id'))

def notify_user(user_id, event_id):
    logging.info("Notifying user %s about event %s", user_id, event_id)
    # Only send notifications for Mike for now
    user = users.User.get_by_id(user_id)
    if not user:
        logging.error("No user found: %s", user_id)
        return
    if user.expired_oauth_token:
        logging.info("User has expired token, aborting: %s", user_id)
        return

    # Only send notifications if the user has RSVP-ed as attending:
    if not _is_attending(user, event_id):
        logging.info("User not attending event, aborting.")
        return

    event = eventdata.DBEvent.get_by_id(event_id)
    if not event:
        logging.error("No event found: %s", event_id)
        return
    event_name = event.fb_event['info']['name']
    event_time = event.start_time.strftime('%H:%M')
    text = '%s: %s' % (event_time, event_name)
    title = 'Upcoming Event!'
    if android.notify(user, event, title, text):
        logging.info("Sent notification!")

    # TODO: iphone_notify!
