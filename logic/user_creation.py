import datetime
import logging
import urllib

from google.appengine.api import taskqueue

import fb_api
from events import users
from logic import backgrounder

def create_user_with_fbuser(fb_uid, fb_user, access_token, access_token_expires, location, send_email=False, referer=None, client=None):
    user = users.User(key_name=str(fb_uid))
    user.fb_access_token = access_token
    user.fb_access_token_expires = access_token_expires
    user.location = location

    # grab the cookie to figure out who referred this user
    logging.info("Referer was: %s", referer)
    if referer:
        user.inviting_fb_uid = int(referer)
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
    #fb_reloading.load_potential_events_for_user_ids(fbl, [fb_uid])
    backgrounder.load_potential_events_for_users([fb_uid])

    return user


def create_user(access_token, access_token_expires, location, send_email=False, referer=None, client=None):
    #TODO(lambebrt): move to servlets/api.py code, combine with initialize() there
    # Build a cache-less lookup
    fbl = fb_api.FBLookup(None, access_token)
    fbl.make_passthrough()
    fb_user = fbl.get(fb_api.LookupUser, 'me')
    user_id = fb_user['profile']['id']
    logging.info("User ID %s", user_id)

    # Move this functionality outside of create_user, since we aren't creating a user.
    user = users.User.get_by_key_name(str(user_id))
    if user:
        logging.info("User exists, updating user with new fb access token data")
        user.fb_access_token = access_token
        user.fb_access_token_expires = access_token_expires
        user.expired_oauth_token = False
        user.expired_oauth_token_reason = ""
        user.put() # this also sets to memcache
        return user
    else:
        fbl = fb_api.FBLookup(user_id, access_token)
        fb_user = fbl.get(fb_api.LookupUser, user_id)
        return create_user_with_fbuser(user_id, fb_user, access_token, access_token_expires, location, send_email=send_email, referer=referer, client=client)

