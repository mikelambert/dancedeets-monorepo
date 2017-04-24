import logging
import time

from google.appengine.ext import ndb

import fb_api
from . import users

def get_multiple_tokens(token_count):
    good_users = users.User.query(users.User.key >= ndb.Key(users.User, '701004'), users.User.expired_oauth_token == False).fetch(token_count)  # noqa
    guaranteed_users = [x for x in good_users if x.fb_uid == '701004']
    if guaranteed_users:
        guaranteed_user_token = guaranteed_users[0].fb_access_token
    else:
        guaranteed_user_token = None
    tokens = [x.fb_access_token for x in good_users]
    debug_token_infos = fb_api.lookup_debug_tokens(tokens)
    some_future_time = time.time() + 7 * (24 * 60 * 60)
    # Ensure our tokens are really still valid, and still valid a few days from now, for long-running mapreduces
    good_tokens = []
    for token, info in zip(tokens, debug_token_infos):
        if info['empty']:
            logging.error('Trying to lookup invalid access token: %s', token)
            continue
        if (info['token']['data']['is_valid'] and
            (info['token']['data']['expires_at'] == 0 or  # infinite token
             info['token']['data']['expires_at'] > some_future_time)):
            good_tokens.append(token)
    # Only trim out the guaranteed-token if we have some to spare
    if len(good_tokens) > 1:
        good_tokens = [x for x in good_tokens if x != guaranteed_user_token]
    return good_tokens
