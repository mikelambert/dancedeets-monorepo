# -*-*- encoding: utf-8 -*-*-

import datetime
import iso3166
import json
import logging
import oauth2 as oauth
import random
import re
import time
import traceback
import urlparse

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
import twitter

from events import eventdata
import fb_api
import fb_api_util
import keys
from users import users
from util import fetch
from util import text
from util import urls

consumer_key = 'xzpiBnUCGqTWSqTgmE6XtLDpw'
consumer_secret = keys.get("twitter_consumer_secret")

DATE_FORMAT = "%Y/%m/%d"
TIME_FORMAT = "%H:%M"

EVENT_PULL_QUEUE = 'event-publishing-pull-queue'


def eventually_publish_event(event_id, token_nickname=None):
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if not db_event.has_content():
        return
    if (db_event.end_time or db_event.start_time) < datetime.datetime.now():
        return

    args = []
    if token_nickname:
        args.append(OAuthToken.token_nickname == token_nickname)
    oauth_tokens = OAuthToken.query(OAuthToken.valid_token == True, *args).fetch(100)
    q = taskqueue.Queue(EVENT_PULL_QUEUE)
    for token in oauth_tokens:
        logging.info("Evaluating token %s", token)
        if _should_post_event(token, db_event):
            logging.info("Adding task for posting!")
            # Names are limited to r"^[a-zA-Z0-9_-]{1,500}$"
            name = 'Token_%s__Event_%s__TimeAdd_%s' % (token.queue_id(), event_id.replace(':', '-'), int(time.time()))
            logging.info("Adding task with name %s", name)
            q.add(taskqueue.Task(name=name, payload=event_id, method='PULL', tag=token.queue_id()))


def _should_post_event(auth_token, db_event):
    geocode = db_event.get_geocode()
    if not geocode:
        # Don't post events without a location. It's too confusing...
        return False
    event_country = geocode.country()
    if auth_token.country_filters and event_country not in auth_token.country_filters:
        logging.info("Skipping event due to country filters")
        return False
    # Additional filtering for FB Wall postings, since they are heavily-rate-limited by FB.
    if auth_token.application == APP_FACEBOOK_WALL:
        if not db_event.is_fb_event:
            logging.info("Event is not FB event")
            return False
        if db_event.is_page_owned:
            logging.info("Event is not owned by page")
            return False
        if not db_event.public:
            logging.info("Event is not public")
            return False
        if db_event.attendee_count < 20:
            logging.warning("Skipping event due to <20 attendees: %s", db_event.attendee_count)
            return False
        if db_event.attendee_count > 600:
            logging.warning("Skipping event due to 600+ attendees: %s", db_event.attendee_count)
            return False
        invited = fb_api.get_all_members_count(db_event.fb_event)
        if invited < 200:
            logging.warning("Skipping event due to <200 invitees: %s", invited)
            return False
        if invited > 2000:
            logging.warning("Skipping event due to 2000+ invitees: %s", invited)
            return False
    logging.info("Publishing event %s with latlng %s", db_event.id, geocode)
    return True


def _get_posting_user(db_event):
    # STR_ID_MIGRATE
    if db_event.creating_fb_uid and db_event.creating_fb_uid != 701004:
        user = users.User.get_by_id(str(db_event.creating_fb_uid))
        name = user.full_name
        return name
    else:
        return None


def post_on_event_wall(db_event):
    logging.info("Considering posting on event wall for %s", db_event.id)
    fbl = get_dancedeets_fbl()
    if not fbl:
        logging.error("Failed to find DanceDeets page access token.")
        return

    url = campaign_url(db_event.id, 'fb_event_wall')
    name = _get_posting_user(db_event) or "we've"
    messages = [
        ('Congrats, %(name)s added this dance event to DanceDeets, the site for street dance events worldwide! '
         'Dancers can discover this event in our DanceDeets mobile app, or on our website here: %(url)s'),
        ('Yay, %(name)s included your event on our DanceDeets website and mobile app for interested dancers. '
         'You can check it out here, and good luck with your event! %(url)s'),
        ('Hey there, %(name)s listed this event on DanceDeets, the website/mobile-app for street dancers worldwide. '
         "We're sure you'll have a great event, but we hope our site can help with that in a small way... %(url)s"),
        ('Awesome, %(name)s added your street dance event to DanceDeets, to help more dancers discover it. '
         "Hopefully you don't mind the extra help in promoting your event! %(url)s"),
    ]
    message = random.choice(messages) % {'name': name, 'url': url}
    logging.info("Attempting to post on event wall for %s", db_event.id)
    result = fbl.fb.post('v2.5/%s/feed' % db_event.fb_event_id, None, {
        'message': message,
        'link': url,
    })
    return result


def pull_and_publish_event():
    oauth_tokens = OAuthToken.query(
        OAuthToken.valid_token == True,
        ndb.OR(
            OAuthToken.next_post_time < datetime.datetime.now(),
            OAuthToken.next_post_time == None
        )
    ).fetch(100)
    q = taskqueue.Queue(EVENT_PULL_QUEUE)
    for token in oauth_tokens:
        logging.info("Can post to OAuthToken: %s", token)
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
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if not db_event:
        logging.warning("Failed to post event: %s, dbevent deleted in dancedeets", event_id)
        return
    if not db_event.has_content():
        logging.warning("Failed to post event: %s, due to %s", event_id, db_event.empty_reason)
        return
    try:
        _post_event(auth_token, db_event)
    except Exception as e:
        logging.exception("Facebook Post Exception: %s", e)
        logging.error(traceback.format_exc())


def _post_event(auth_token, db_event):
    if auth_token.application == APP_TWITTER:
        twitter_post(auth_token, db_event)
    elif auth_token.application == APP_FACEBOOK:
        result = facebook_post(auth_token, db_event)
        if 'error' in result:
            logging.error("Facebook Post Error: %r", result)
        else:
            logging.info("Facebook result was %r", result)
    elif auth_token.application == APP_FACEBOOK_WALL:
        result = post_on_event_wall(db_event)
        if result:
            if 'error' in result:
                logging.error("Facebook WallPost Error: %r", result)
            else:
                logging.info("Facebook result was %r", result)
    else:
        logging.error("Unknown application for OAuthToken: %s", auth_token.application)

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


def campaign_url(eid, source):
    return urls.dd_event_url(eid, {
        'utm_source': source,
        'utm_medium': 'share',
        'utm_campaign': 'autopost'
    })

TWITTER_CONFIG_KEY = 'TwitterConfig'
TWITTER_CONFIG_EXPIRY = 24 * 60 * 60


def get_twitter_config(t):
    config = memcache.get(TWITTER_CONFIG_KEY)
    if config:
        return json.loads(config)
    config = t.help.configuration()
    memcache.set(TWITTER_CONFIG_KEY, json.dumps(config), TWITTER_CONFIG_EXPIRY)
    return config


def format_twitter_post(config, db_event, media, handles=None):
    url = campaign_url(db_event.id, 'twitter_feed')
    title = db_event.name
    city = db_event.actual_city_name

    datetime_string = db_event.start_time.strftime(DATE_FORMAT)

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
        auth=twitter.OAuth(auth_token.oauth_token, auth_token.oauth_token_secret, consumer_key, consumer_secret))

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
        handles = list(set(twitter_handles + twitter_handles2))
    else:
        handles = []
    config = get_twitter_config(t)
    status = format_twitter_post(config, db_event, media, handles=handles)
    t.statuses.update(status=status, **update_params)


class LookupGeoTarget(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, urlparams):
        return [
            ('search', cls.url('search?type=adgeolocation&%s' % urlparams)),
        ]

    @classmethod
    def cache_key(cls, query, fetching_uid):
        return (fb_api.USERLESS_UID, query, 'OBJ_GEO_TARGET')


def facebook_post(auth_token, db_event):
    link = campaign_url(db_event.id, 'fb_feed')
    datetime_string = db_event.start_time.strftime('%s @ %s' % (DATE_FORMAT, TIME_FORMAT))

    page_id = auth_token.token_nickname
    endpoint = 'v2.8/%s/feed' % page_id
    fbl = fb_api.FBLookup(None, auth_token.oauth_token)

    post_values = {}
    # post_values['message'] = db_event.name
    post_values['link'] = link
    post_values['name'] = db_event.name
    post_values['caption'] = datetime_string
    name = _get_posting_user(db_event)

    human_date = db_event.start_time.strftime('%B %-d')
    # TODO: Sometimes we definitely know the City (from a lat/long), but FB doesn't give us a city.
    # Hopefully in the Great Event Location Cleanup, can take care of this...
    if db_event.city:
        location = db_event.city
    else:
        location = ''

    host = ''
    admins = db_event.admins
    if admins:
        admin_ids = [x['id'] for x in admins]
        page_admin_ids = fb_api_util.filter_by_type(fbl, admin_ids, 'page')
        host = text.human_list('@[%s]' % x for x in page_admin_ids)

    # Tag it if we can
    if db_event.venue.get('id'):
        venue = '@[%s]' % db_event.venue.get('id')
    else:
        venue = db_event.location_name

    params = {
        'location': ' ' + location if location else '',
        'date': human_date,
        'venue': venue,
    }
    messages = [
        'Hey%(location)s dancers, mark your calendars! We just found a new dance event on %(date)s at %(venue)s.',
        'Hey%(location)s dancers, save the date! Look what we found coming up on %(date)s at %(venue)s.',
        'Hey%(location)s, upcoming dance event on %(date)s at %(venue)s.',
    ]
    message = random.choice(messages) % params
    if host and host != venue:
        message += ' Hosted by our friends at %s.' % host
    if name:
        message += ' Thanks to %s for adding it to DanceDeets!' % name
    post_values['message'] = message

    description = db_event.description
    if len(description) > 10000:
        post_values['description'] = description[:9999] + u"…"
    else:
        post_values['description'] = description
    post_values['description'] = post_values['description']
    cover = db_event.largest_cover
    if cover:
        post_values['picture'] = cover['source']
    venue_id = db_event.venue.get('id')
    if venue_id:
        post_values['place'] = venue_id

    feed_targeting = get_targeting_data(fbl, db_event)
    if feed_targeting:
        # Ideally we'd do this as 'feed_targeting', but Facebook appears to return errors with that due to:
        # {u'error': {u'message': u'Invalid parameter', u'code': 100, u'is_transient': False,
        #  u'error_user_title': u'Invalid Connection', u'error_subcode': 1487124, u'type': u'FacebookApiException',
        #  u'error_user_msg': u'You can only specify connections to objects you are an administrator or developer of.',
        #  u'error_data': {u'blame_field': u'targeting'}}}
        post_values['targeting'] = json.dumps(feed_targeting)

    logging.info("FB Feed Post Values: %s", post_values)
    return fbl.fb.post(endpoint, None, post_values)


def get_targeting_data(fbl, db_event):
    city_key = None

    short_country = db_event.country
    if short_country:
        city_state_list = [
            db_event.city,
            db_event.state,
        ]
        city_state = ', '.join(x for x in city_state_list if x)
        geo_search = {
            'type': 'adgeolocation',
            'location_types': 'city',
            'country_code': db_event.country,
            'q': city_state,
        }
        geo_target = fbl.get(LookupGeoTarget, urls.urlencode(geo_search), allow_cache=False)

        good_targets = geo_target['search']['data']
        if good_targets:
            # Is usually an integer, but in the case of HK and SG (city/country combos), it can be a string
            city_key = good_targets[0]['key']
            # if we want state-level targeting, 'region_id' would be the city's associated state

    if not short_country:
        geocode = db_event.get_geocode()
        if geocode:
            short_country = geocode.country()

    feed_targeting = {}
    # Target by city if we can, otherwise use the country
    if city_key:
        feed_targeting['cities'] = [{'key': city_key}]
    elif short_country:
        feed_targeting['countries'] = [short_country]
    full_targeting = {'geo_locations': feed_targeting}
    return full_targeting


request_token_url = 'https://twitter.com/oauth/request_token'
access_token_url = 'https://twitter.com/oauth/access_token'
authorize_url = 'https://twitter.com/oauth/authorize'

APP_TWITTER = 'APP_TWITTER'
APP_FACEBOOK = 'APP_FACEBOOK'  # a butchering of OAuthToken!
APP_FACEBOOK_WALL = 'APP_FACEBOOK_WALL'  # a further butchering!


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

    json_data = ndb.JsonProperty()

    # search criteria? location? radius? search terms?
    # post on event find? post x hours before event? multiple values?

    def queue_id(self):
        return str(self.key.id())

    @property
    def country_filters(self):
        if self.json_data is None:
            self.json_data = {}
        return self.json_data.setdefault('country_filters', [])


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

    auth_tokens = OAuthToken.query(
        OAuthToken.user_id == user_id,
        OAuthToken.token_nickname == token_nickname,
        OAuthToken.application == APP_TWITTER
    ).fetch(1)
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
        auth_token.country_filters += country_filter.upper()
    auth_token.put()

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.

    return "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])

# user comes to:
# /sign-in-with-twitter/?
#        oauth_token=NPcudxy0yU5T3tBzho7iCotZ3cnetKwcTIRlX0iwRl0&
#        oauth_verifier=uw7NjWHT6OJ1MpJOXsHfNxoAhPKpgI8BlYDhxEjIBY


def twitter_oauth2(oauth_token, oauth_verifier):
    auth_tokens = OAuthToken.query(
        OAuthToken.temp_oauth_token == oauth_token,
        OAuthToken.application == APP_TWITTER
    ).fetch(1)
    if not auth_tokens:
        return None
    auth_token = auth_tokens[0]
    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(oauth_token, auth_token.temp_oauth_token_secret)
    token.set_verifier(oauth_verifier)
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    auth_token.oauth_token = access_token['oauth_token']
    auth_token.oauth_token_secret = access_token['oauth_token_secret']
    auth_token.valid_token = True
    auth_token.time_between_posts = 5 * 60 # every 5 minutes
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


def get_dancedeets_fbl():
    page_id = '110312662362915'
    #page_id = '1375421172766829'
    tokens = OAuthToken.query(OAuthToken.user_id == '701004', OAuthToken.token_nickname == page_id, OAuthToken.application == APP_FACEBOOK).fetch(1)
    if tokens:
        return fb_api.FBLookup(None, tokens[0].oauth_token)
    else:
        return None


def facebook_auth(fbl, page_uid, country_filter):
    accounts = fbl.get(LookupUserAccounts, fbl.fb_uid, allow_cache=False)
    all_pages = accounts['accounts']['data']
    pages = [x for x in all_pages if x['id'] == page_uid]
    if not pages:
        raise ValueError("Failed to find page id in user's page permissions: %s" % page_uid)
    page = pages[0]
    page_token = page['access_token']

    auth_tokens = OAuthToken.query(OAuthToken.user_id == fbl.fb_uid, OAuthToken.token_nickname == page_uid, OAuthToken.application == APP_FACEBOOK).fetch(1)
    if auth_tokens:
        auth_token = auth_tokens[0]
    else:
        auth_token = OAuthToken()
    auth_token.user_id = fbl.fb_uid
    auth_token.token_nickname = page_uid
    auth_token.application = APP_FACEBOOK
    auth_token.valid_token = True
    auth_token.oauth_token = page_token
    auth_token.time_between_posts = 5 * 60
    if country_filter:
        auth_token.country_filters += country_filter.upper()
    auth_token.put()
    return auth_token
