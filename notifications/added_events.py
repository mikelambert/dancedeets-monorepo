import datetime
import logging

import app
import base_servlet
from loc import gmaps_api
from search import search
from search import search_base
from users import users
from util import dates
from util import math
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

# TODO: call hourly
@app.route('/tasks/promote_new_events')
class RemindUserHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        pass
        # called hourly:
        #mapreduce.start(
        #    offset=get_time_offset(),
        #    call_func=promote_events_to_user)

# for development only, usually this will be called via mapreduce
@app.route('/tasks/promote_events_to_user')
class RemindUserHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        promote_events_to_user(self.request.get('user_id'))

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
    query = search_base.SearchQuery(time_period=dates.TIME_FUTURE, bounds=bounds, min_attendees=min_attendees)

    one_day_ago = datetime.datetime.now() - datetime.timedelta(hours=24)

    search_query = search.Search(query)
    search_query.extra_fields = ['creation_time']
    search_results = search_query._get_candidate_doc_events()
    # TODO: can we move this filter into the search query itself??
    recent_events = [x.field('doc_id') for x in search_results if x.field('creation_time').value > one_day_ago]

    for event_id in recent_events:
        if android.notify(user, event_id):
            logging.info("Sent notification! %s", event_id)
    # TODO: iphone_notify!

