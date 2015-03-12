# -*-*- encoding: utf-8 -*-*-

import datetime
import iso3166
import json
import logging
import oauth2 as oauth
import re
import time
import urllib
import urlparse

from google.appengine.ext import ndb
import twitter

from events import eventdata
from events import event_locations
import fb_api
import keys
from util import dates
from util import fetch
from util import urls

consumer_key = 'xzpiBnUCGqTWSqTgmE6XtLDpw'
consumer_secret = keys.get("twitter_consumer_secret") 

DATE_FORMAT = "%Y/%m/%d"
TIME_FORMAT = "%H:%M"

from google.appengine.api import taskqueue

EVENT_PULL_QUEUE = 'event-publishing-pull-queue'

def eventually_publish_event(event_id, token_nickname=None):
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if db_event.fb_event['empty']:
        return
    if dates.parse_fb_end_time(db_event.fb_event, need_result=True) < datetime.datetime.now():
        return
    location_info = event_locations.LocationInfo(db_event.fb_event, db_event)
    logging.info("Publishing event %s with latlng %s", event_id, location_info.geocode)
    if not location_info.geocode:
        # Don't post events without a location. It's too confusing...
        return
    event_country = location_info.geocode.country()

    args = []
    if token_nickname:
        args.append(OAuthToken.token_nickname==token_nickname)
    oauth_tokens = OAuthToken.query(OAuthToken.valid_token==True, *args).fetch(100)
    q = taskqueue.Queue(EVENT_PULL_QUEUE)
    for token in oauth_tokens:
        logging.info("Evaluating token %s", token)
        if token.country_filter:
            if event_country != token.country_filter:
                continue
        logging.info("Adding task for posting!")
        # Names are limited to r"^[a-zA-Z0-9_-]{1,500}$"
        name = 'Token_%s__Event_%s__TimeAdd_%s' % (token.queue_id(), event_id, int(time.time()))
        logging.info("Adding task with name %s", name)
        q.add(taskqueue.Task(name=name, payload=event_id, method='PULL', tag=token.queue_id()))

def pull_and_publish_event():
    oauth_tokens = OAuthToken.query(
        OAuthToken.valid_token==True,
        ndb.OR(
            OAuthToken.next_post_time<datetime.datetime.now(),
            OAuthToken.next_post_time==None
        )
    ).fetch(100)
    q = taskqueue.Queue(EVENT_PULL_QUEUE)
    for token in oauth_tokens:
        logging.info("Posting to OAuthToken: %s", token)
        tasks = q.lease_tasks_by_tag(120, 1, token.queue_id())
        logging.info("Fetching %d tasks with queue id %s", len(tasks), token.queue_id())
        if tasks:
            for task in tasks:
                event_id = task.payload
                logging.info("  Found event, posting %s", event_id)
                post_event_id_with_authtoken(event_id, token)
                q.delete_tasks(task)
            next_post_time = datetime.datetime.now() + datetime.timedelta(seconds=token.time_between_posts)
            token = token.key.get()
            token.next_post_time = next_post_time
            token.put()

def post_event_id_with_authtoken(event_id, auth_token):
    event_id = event_id
    db_event = eventdata.DBEvent.get_or_insert(event_id)
    if db_event.fb_event['empty']:
        logging.warning("Failed to post event: %s, due to %s", event_id, db_event.fb_event['empty'])
        return
    if auth_token.application == APP_TWITTER:
        try:
            twitter_post(auth_token, db_event)
        except Exception as e:
            logging.error("Twitter Post Error: %s", e)
    elif auth_token.application == APP_FACEBOOK:
        try:
            result = facebook_post(auth_token, db_event)
            if 'error' in result:
                logging.error("Facebook Post Error: %r", result)
            else:
                logging.info("Facebook result was %r", result)
        except Exception as e:
            logging.exception("Facebook Post Exception: %s", e)
    else:
        logging.error("Unknown application for OAuthToken: %s", auth_token.application)

def create_media_on_twitter(t, fb_event):
    cover = eventdata.get_largest_cover(fb_event)
    if not cover:
        return None
    mimetype, response = fetch.fetch_data(cover['source'])
    try:
        t.domain = 'upload.twitter.com'
        result = t.media.upload(media=response)
    finally:
        t.domain = 'api.twitter.com'
    return result

def format_twitter_post(db_event, fb_event, media, handles=None):
    url = urls.fb_event_url(fb_event['info']['id'])
    title = fb_event['info']['name']
    city = db_event.actual_city_name

    start_time = dates.parse_fb_start_time(fb_event)
    #TODO(lambert): Some day, when we are doing more local relevant data, list the time here, and do it at the right time accounting for timezone offsets
    #if start_time.date() == datetime.date.today():
    #    datetime_string = start_time.strftime(TIME_FORMAT)
    #else:
    datetime_string = start_time.strftime(DATE_FORMAT)

    # The "short_url_length" is 22, so I use 23 for the space beforehand.
    # TODO(lambert): fetch help/configuration.json daily to find the current value
    # as described on https://dev.twitter.com/overview/t.co
    url_length = 23
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

    num_urls = 1
    if media:
        num_urls += 1 # the "characters_reserved_per_media" is '23', which is 22 + 1 space

    title_length = 140 - len(prefix) - len(u"…") - url_length*num_urls - len(handle_string)
    final_title = title[0:title_length]
    if final_title != title:
        final_title += u'…'
    return u"%s%s %s%s" % (prefix, final_title, url, handle_string)

def twitter_post(auth_token, db_event):
    t = twitter.Twitter(
        auth=twitter.OAuth(auth_token.oauth_token, auth_token.oauth_token_secret, consumer_key, consumer_secret))

    update_params = {}
    if db_event.latitude:
        update_params['lat'] = db_event.latitude
        update_params['long'] = db_event.longitude

    media = create_media_on_twitter(t, db_event.fb_event)
    if media:
        update_params['media_ids'] = media['media_id']


    description = db_event.fb_event['info'].get('description') or ''
    twitter_handles = re.findall(r'\s@[A-za-z0-9_]+', description)
    twitter_handles = [x.strip() for x in twitter_handles if len(x) <= 1+15]
    twitter_handles2 = re.findall(r'twitter\.com/([A-za-z0-9_]+)', description)
    twitter_handles2 = ['@%s' % x.strip() for x in twitter_handles2 if len(x) <= 1+15]
    # This is the only twitter account allowed to @mention, to avoid spamming everyone...
    if auth_token.token_nickname == 'BigTwitter':
        handles = (twitter_handles + twitter_handles2)
    else:
        handles = []
    status = format_twitter_post(db_event, db_event.fb_event, media, handles=handles)
    t.statuses.update(status=status, **update_params)


class LookupGeoTarget(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, query):
        return [
            ('search', cls.url('search?type=adgeolocation&q=%s' % urllib.quote(query))),
        ]
    @classmethod
    def cache_key(cls, query, fetching_uid):
        return (fb_api.USERLESS_UID, query, 'OBJ_GEO_TARGET')

def facebook_post(auth_token, db_event):
    fb_event = db_event.fb_event
    link = urls.fb_event_url(fb_event['info']['id'])
    start_time = dates.parse_fb_start_time(fb_event)
    datetime_string = start_time.strftime('%s @ %s' % (DATE_FORMAT, TIME_FORMAT))

    page_id = auth_token.token_nickname
    endpoint = '/v2.2/%s/feed' % page_id
    fbl = fb_api.FBLookup(None, auth_token.oauth_token)

    post_values = {}
    #post_values['message'] = fb_event['info']['name']
    post_values['link'] = link
    post_values['name'] = fb_event['info']['name'].encode('utf8')
    post_values['caption'] = datetime_string
    description = fb_event['info'].get('description', '')
    if len(description) > 10000:
        post_values['description'] = description[:9999] + u"…"
    else:
        post_values['description'] = description
    post_values['description'] = post_values['description'].encode('utf8')
    cover = eventdata.get_largest_cover(fb_event)
    if cover:
        post_values['picture'] = cover['source']
    venue_id = fb_event['info'].get('venue', {}).get('id')
    short_country = None
    city_key = None
    region_key = None
    if venue_id:
        post_values['place'] = venue_id
        # Can only tag people if there is a place tagged too
        if fb_event['info'].get('admins'):
            admin_ids = [x['id'] for x in fb_event['info']['admins']['data']]
            post_values['tags'] = ','.join(admin_ids)

        # Target to people in the same country as the event. Should improve signal/noise ratio.
        country = fb_event['info']['venue'].get('country')
        if country:
            country = country.upper()
            if country in iso3166.countries_by_name:
                short_country = iso3166.countries_by_name[country].alpha2

        # only do city-level targeting in big countries or dense dance countries
        # we don't do city-level targeting, as we can only do a 50 mile radius on that
        if short_country in ['US', 'CA', 'RU', 'JP']:
            city_state_country_list = [fb_event['info']['venue'].get('city')]
            # Strange search logic behavior I noticed in my test searches of facebook.
            # Country is not needed (and detrimental!) when searching for a US city.
            if short_country == 'US':
                city_state_country_list.append(fb_event['info']['venue'].get('state'))
            else:
                city_state_country_list.append(fb_event['info']['venue'].get('country'))
            city_state_country = ', '.join(x for x in city_state_country_list if x)
            geo_target = fbl.get(LookupGeoTarget, city_state_country)
            if short_country in 'US':
                state = fb_event['info']['venue'].get('state')
                # CA is a big state, so do city-level targeting
                # NK/NJ are also lopsided states, where NJ/NY overlap in location interests.
                # We could potentially list multiple zip codes, or states, or cities, but that's getting complex...
                if state in ['CA', 'NY', 'NJ', 'PA']:
                    good_targets = [x for x in geo_target['search']['data'] if x['supports_region']]
                    if good_targets:
                        # They give it to us as an integer, but the API doc example says they want a string
                        region_key = str(good_targets[0]['region_id'])
                else:
                    good_targets = [x for x in geo_target['search']['data'] if x['supports_city']]
                    if good_targets:
                        city_key = good_targets[0]['key']

    if not short_country:
        location_info = event_locations.LocationInfo(fb_event, db_event)
        if location_info.geocode:
            short_country = location_info.geocode.country()

    feed_targeting = {}
    if short_country:
        feed_targeting['countries'] = [short_country]
        if city_key:
            feed_targeting['cities'] = [{'key': city_key, 'radius': 50, 'distance_unit': 'mile'}]
        if region_key:
            feed_targeting['regions'] = [{'key': region_key}]
    if feed_targeting:
        post_values['feed_targeting'] = json.dumps(feed_targeting)

    print post_values
    result = fbl.fb.post(endpoint, None, post_values)
    return json.loads(result)


request_token_url = 'https://twitter.com/oauth/request_token'
access_token_url = 'https://twitter.com/oauth/access_token'
authorize_url = 'https://twitter.com/oauth/authorize'

APP_TWITTER = 'APP_TWITTER'
APP_FACEBOOK = 'APP_FACEBOOK' # a butchering of OAuthToken!
#...instagram?
#...tumblr?

class OAuthToken(ndb.Model):
    user_id = ndb.StringProperty()
    token_nickname = ndb.StringProperty()
    application = ndb.StringProperty()
    temp_oauth_token = ndb.StringProperty()
    temp_oauth_token_secret = ndb.StringProperty()
    valid_token = ndb.BooleanProperty()
    oauth_token = ndb.StringProperty()
    oauth_token_secret = ndb.StringProperty()

    time_between_posts = ndb.IntegerProperty() # In seconds!
    next_post_time = ndb.DateTimeProperty()

    # TODO(lambert): Fix this temp hack by implementing proper list-of-filters in json
    # For the moment, use a two-character country code here.
    country_filter = ndb.StringProperty()

    #search criteria? location? radius? search terms?
    #post on event find? post x hours before event? multiple values?

    def queue_id(self):
        return str(self.key.id())


def twitter_oauth1(user_id, token_nickname, country_filter):
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for 
    # having the user authorize an access token and to sign the request to obtain 
    # said access token.

    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    auth_tokens = OAuthToken.query(OAuthToken.user_id==user_id, OAuthToken.token_nickname==token_nickname, OAuthToken.application==APP_TWITTER).fetch(1)
    if auth_tokens:
        auth_token = auth_tokens[0]
    else:
        auth_token = OAuthToken()
    auth_token.user_id = user_id
    auth_token.token_nickname = token_nickname
    auth_token.application = APP_TWITTER
    auth_token.temp_oauth_token = request_token['oauth_token']
    auth_token.temp_oauth_token_secret = request_token['oauth_token_secret']
    if country_filter:
        auth_token.country_filter = country_filter.upper()
    auth_token.put()

    # Step 2: Redirect to the provider. Since this is a CLI script we do not 
    # redirect. In a web application you would redirect the user to the URL
    # below.

    return "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])

#user comes to:
#/sign-in-with-twitter/?
#        oauth_token=NPcudxy0yU5T3tBzho7iCotZ3cnetKwcTIRlX0iwRl0&
#        oauth_verifier=uw7NjWHT6OJ1MpJOXsHfNxoAhPKpgI8BlYDhxEjIBY

def twitter_oauth2(oauth_token, oauth_verifier):
    auth_tokens = OAuthToken.query(OAuthToken.temp_oauth_token==oauth_token, OAuthToken.application==APP_TWITTER).fetch(1)
    if not auth_tokens:
        return None
    auth_token = auth_tokens[0]
    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the 
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this 
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(oauth_token,
        auth_token.temp_oauth_token_secret)
    token.set_verifier(oauth_verifier)
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    auth_token.oauth_token = access_token['oauth_token']
    auth_token.oauth_token_secret = access_token['oauth_token_secret']
    auth_token.valid_token = True
    auth_token.time_between_posts = 5*60
    auth_token.put()
    return auth_token


class LookupUserAccounts(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('accounts', cls.url('%s/accounts' % object_id)),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid, object_id, 'OBJ_USER_ACCOUNTS')


def facebook_auth(fbl, page_uid, country_filter):
    accounts = fbl.get(LookupUserAccounts, fbl.fb_uid, allow_cache=False)
    all_pages = accounts['accounts']['data']
    pages = [x for x in all_pages if x['id'] == page_uid]
    if not pages:
        raise ValueError("Failed to find page id in user's page permissions: %s" % page_uid)
    page = pages[0]
    page_token = page['access_token']

    auth_tokens = OAuthToken.query(OAuthToken.user_id==fbl.fb_uid, OAuthToken.token_nickname==page_uid, OAuthToken.application==APP_FACEBOOK).fetch(1)
    if auth_tokens:
        auth_token = auth_tokens[0]
    else:
        auth_token = OAuthToken()
    auth_token.user_id = fbl.fb_uid
    auth_token.token_nickname = page_uid
    auth_token.application = APP_FACEBOOK
    auth_token.valid_token = True
    auth_token.oauth_token = page_token
    auth_token.time_between_posts = 5*60
    if country_filter:
        auth_token.country_filter = country_filter.upper()
    auth_token.put()
    return auth_token

