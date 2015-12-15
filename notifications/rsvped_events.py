import datetime
import logging
import urllib

from dateutil import parser

from google.appengine.api import taskqueue

import app
import base_servlet
from events import eventdata
from users import users
from util import urls
from . import android

def setup_reminders(fb_uid, fb_user_events):
    results_json = fb_user_events['all_event_info']['data']
    #STR_ID_MIGRATE: We still get ids as ints from our FQL
    event_ids = [str(x['eid']) for x in sorted(results_json, key=lambda x: x.get('start_time'))]

    existing_events = [x for x in eventdata.DBEvent.get_by_ids(event_ids) if x]
    logging.info("For user %s's %s events, %s are real dance events", fb_uid, len(event_ids), len(existing_events))
    for event in existing_events:
        start_time = parser.parse(event.fb_event['info'].get('start_time'))
        # Otherwise it's at a specific time (we need the time with the timezone info included)
        # Also try to get it ten minutes before the Facebook event comes in, so that we aren't seen as the "dupe".
        notify_time = start_time - datetime.timedelta(hours=1, minutes=10)

        # I think 30 days is the limit for appengine tasks with ETA set, but it gets trickier with all the timezones.
        # And really, we run this code multiple times a day, so don't need to plan out more than a single day.
        # Otherwise if the user un-rsvp's for an event, we'll still have a zombie task waiting to notify them.
        # (And AppEngine doesn't like us removing-and-readding a named task item anyway)
        future_cutoff = datetime.datetime.now(notify_time.tzinfo) + datetime.timedelta(days=1)

        if notify_time > future_cutoff:
            continue
        logging.info("For event %s, sending notifications at %s", event.fb_event_id, notify_time)
        try:
            taskqueue.add(
                method='GET',
                name='notify_user-%s-%s' % (fb_uid, event.fb_event_id),
                queue_name='mobile-notify-queue',
                eta=notify_time,
                url='/tasks/notify_user?'+urllib.urlencode(dict(
                    user_id=fb_uid,
                    event_id=event.fb_event_id)),
            )
        except taskqueue.TaskAlreadyExistsError:
            pass

@app.route('/tasks/notify_user')
class NotifyUserHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        notify_user(self.request.get('user_id'), self.request.get('event_id'))

def notify_user(user_id, event_id):
    logging.info("Sending notifications to user %s about event %s", user_id, event_id)
    # Only send notifications for Mike for now
    if user_id != '701004':
        return
    user = users.User.get_by_id(user_id)
    event = eventdata.DBEvent.get_by_id(event_id)
    event_name = event.fb_event['info']['name']
    event_time = event.start_time.strftime('%H:%M')
    text = '%s: %s' % (event_time, event_name)
    title = 'Upcoming Event!'
    url = urls.fb_event_url(event_id)
    android.notify(user, title, text, url)
    # TODO: iphone_notify!
