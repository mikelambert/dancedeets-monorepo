import datetime
import logging
import urllib

from google.appengine.api import taskqueue

from logic import backgrounder
from . import users

def create_user_with_fbuser(fb_uid, fb_user, access_token, access_token_expires, location, send_email=False, referer=None, client=None):
    user = users.User(key_name=fb_uid)
    user.fb_access_token = access_token
    user.fb_access_token_expires = access_token_expires
    user.location = location

    # grab the cookie to figure out who referred this user
    logging.info("Referer was: %s", referer)
    if referer:
        #STR_ID_MIGRATE
        user.inviting_fb_uid = long(referer)
    user.clients = [client]

    user.send_email = send_email
    user.distance = '50'
    user.distance_units = 'miles'
    user.min_attendees = 0

    user.creation_time = datetime.datetime.now()

    user.login_count = 1
    user.last_login_time = user.creation_time

    user.compute_derived_properties(fb_user)
    logging.info("Saving user with name %s", user.full_name)
    user.put()

    logging.info("Requesting background load of user's friends")
    # Must occur after User is put with fb_access_token
    taskqueue.add(method='GET', url='/tasks/track_newuser_friends?' + urllib.urlencode({'user_id': fb_uid}), queue_name='slow-queue')
    # Now load their potential events, to make "add event page" faster (and let us process/scrape their events)
    #potential_events_reloading.load_potential_events_for_user_ids(fbl, [fb_uid])
    backgrounder.load_potential_events_for_users([fb_uid])

    return user

