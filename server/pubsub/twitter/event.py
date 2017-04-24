# -*-*- encoding: utf-8 -*-*-

import json
import re

from google.appengine.api import memcache

from util import fetch
import twitter
from .. import common
from . import auth

TWITTER_CONFIG_KEY = 'TwitterConfig'
TWITTER_CONFIG_EXPIRY = 24 * 60 * 60

def create_media_on_twitter(t, db_event):
    cover = db_event.largest_cover
    if not cover:
        return None
    mimetype, response = fetch.fetch_data(cover['source'])
    try:
        t.domain = 'upload.twitter.com'
        result = t.media.upload(media=response)
    finally:
        t.domain = 'api.twitter.com'
    return result

def get_twitter_config(t):
    config = memcache.get(TWITTER_CONFIG_KEY)
    if config:
        return json.loads(config)
    config = t.help.configuration()
    memcache.set(TWITTER_CONFIG_KEY, json.dumps(config), TWITTER_CONFIG_EXPIRY)
    return config


def format_twitter_post(config, db_event, media, handles=None):
    url = common.campaign_url(db_event.id, 'twitter_feed')
    title = db_event.name
    city = db_event.actual_city_name

    datetime_string = db_event.start_time.strftime(common.DATE_FORMAT)

    short_url_length = config['short_url_length']
    characters_reserved_per_media = config['characters_reserved_per_media']
    url_length = short_url_length + 1
    prefix = ''
    prefix += "%s: " % datetime_string
    if city:
        prefix += '%s: ' % city

    if handles:
        handle_string = ''
        for handle in handles:
            new_handle_string = '%s %s' % (handle_string, handle)
            if len(new_handle_string) >= 40:
                break
            handle_string = new_handle_string
    else:
        handle_string = ''

    title_length = 140 - len(prefix) - len(u"…") - url_length - len(handle_string)
    if media:
        title_length -= characters_reserved_per_media

    final_title = title[0:title_length]
    if final_title != title:
        final_title += u'…'
    result = u"%s%s %s%s" % (prefix, final_title, url, handle_string)
    return result


def twitter_post(auth_token, db_event):
    t = twitter.Twitter(
        auth=twitter.OAuth(auth_token.oauth_token, auth_token.oauth_token_secret, auth.consumer_key, auth.consumer_secret))

    update_params = {}
    if db_event.latitude:
        update_params['lat'] = db_event.latitude
        update_params['long'] = db_event.longitude

    media = create_media_on_twitter(t, db_event)
    if media:
        update_params['media_ids'] = media['media_id']

    TWITTER_HANDLE_LENGTH = 16
    description = db_event.description
    twitter_handles = re.findall(r'\s@[A-za-z0-9_]+', description)
    twitter_handles = [x.strip() for x in twitter_handles if len(x) <= 1 + TWITTER_HANDLE_LENGTH]
    twitter_handles2 = re.findall(r'twitter\.com/([A-za-z0-9_]+)', description)
    twitter_handles2 = ['@%s' % x.strip() for x in twitter_handles2 if len(x) <= 1 + TWITTER_HANDLE_LENGTH]
    # This is the only twitter account allowed to @mention, to avoid spamming everyone...
    if auth_token.token_nickname == 'BigTwitter':
        # De-dupe these lists
        handles = [x.lower() for x in list(set(twitter_handles + twitter_handles2))]
    else:
        handles = []
    venue_name = (db_event.location_name or '').lower()
    # Remove any handles that are really just "@venue_name"
    handles = [x for x in handles if x not in venue_name]
    config = get_twitter_config(t)
    status = format_twitter_post(config, db_event, media, handles=handles)
    t.statuses.update(status=status, **update_params)

