import datetime
import logging
import time

from mapreduce import control

import app
import base_servlet
from loc import gmaps_api
from loc import math
from search import search
from search import search_base
from users import users
from . import android

"""
Runs a mapreduce hourly, which finds all users with that timezone offset,
and sends notifications about recently-aevents to those users
"""

def get_time_offset():
    desired_hour = 16 # send new-event notifications at 4pm
    current_hour = datetime.datetime.now().hour # should be UTC hour
    offset = desired_hour - current_hour
    if offset <= -12:
        offset += 24
    if offset > 12:
        offset -= 24
    return offset

@app.route('/tasks/promote_new_events')
class RemindUserMapReduceHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        offset = get_time_offset()
        string_offset = '%+03d00' % offset
        logging.info("Got time offset %s for our run", string_offset)
        control.start_map(
            name='Send New Events to Users in TZ%s' % string_offset,
            reader_spec='mapreduce.input_readers.DatastoreInputReader',
            handler_spec='notifications.added_events.promote_events_to_user',
            mapper_parameters={
                'entity_kind': 'users.users.User',
                'filters': [
                    ('timezone_offset', '>=', offset),
                    ('timezone_offset', '<', offset+1),
                ],
            },
            shard_count=1,
        )

# for development only, usually this will be called via mapreduce
@app.route('/tasks/promote_new_events_to_user')
class RemindUserHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        user_id = self.request.get('user_id')
        user = users.User.get_by_id(user_id)
        promote_events_to_user(user)

def promote_events_to_user(user):
    logging.info("Promoting new events to user %s", user.fb_uid)
    # Only send notifications for Mike for now
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
    geocode = gmaps_api.get_geocode(address=user_location)
    if not geocode:
        return None
    bounds = math.expand_bounds(geocode.latlng_bounds(), distance_in_km)
    query = search_base.SearchQuery(time_period=search_base.TIME_UPCOMING, bounds=bounds, min_attendees=min_attendees)

    one_day_ago = time.mktime((datetime.datetime.now() - datetime.timedelta(hours=24)).timetuple())

    search_query = search.Search(query)
    search_query.extra_fields = ['creation_time']
    search_results = search_query._get_candidate_doc_events()
    # TODO: can we move this filter into the search query itself??
    recent_events = [x.doc_id for x in search_results if x.field('creation_time').value > one_day_ago]

    logging.info("Found %s search_results, %s new events", len(search_results), len(recent_events))
    for event_id in recent_events:
        logging.info("Notifying about new event %s", event_id)
        if android.add_notify(user, event_id):
            logging.info("Sent notification! %s", event_id)
    # TODO: iphone_notify!

