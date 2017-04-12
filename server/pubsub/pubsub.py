# -*-*- encoding: utf-8 -*-*-

import datetime
import json
import logging
import random
import re
import time

from google.appengine.ext import ndb

from events import eventdata
import fb_api
import fb_api_util
from users import users
from util import fb_events
from util import taskqueue
from util import text
from . import common
from .twitter import event as twitter_event


EVENT_PULL_QUEUE = 'event-publishing-pull-queue'


def eventually_publish_event(event_id, token_nickname=None):
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if not db_event.has_content():
        logging.info('Not publishing %s because it has no content.', db_event.id)
        return
    if (db_event.end_time or db_event.start_time) < datetime.datetime.now():
        logging.info('Not publishing %s because it is in the past.', db_event.id)
        return

    def should_post(auth_token):
        return _should_post_event(auth_token, db_event)
    return eventually_publish_data(event_id, should_post, token_nickname)

def eventually_publish_city_key(city_key):
    print city_key
    def should_post(auth_token):
        return auth_token.application == APP_FACEBOOK_WEEKLY
    return eventually_publish_data(city_key, should_post)

def eventually_publish_data(data, should_post, token_nickname=None):
    args = []
    if token_nickname:
        args.append(OAuthToken.token_nickname == token_nickname)
    oauth_tokens = OAuthToken.query(OAuthToken.valid_token == True, *args).fetch(100)
    q = taskqueue.Queue(EVENT_PULL_QUEUE)
    for token in oauth_tokens:
        logging.info("Evaluating token %s", token)
        if should_post(token):
            logging.info("Adding task for posting!")
            # Names are limited to r"^[a-zA-Z0-9_-]{1,500}$"
            time_add = int(time.time()) if token.allow_reposting else 0
            # "Event" here is a misnamer...but we leave it for now.
            sanitized_data = re.sub(r'[^a-zA-Z0-9_-]', '-', data)
            name = 'Token_%s__Event_%s__TimeAdd_%s' % (token.queue_id(), sanitized_data, time_add)
            logging.info("Adding task with name %s", name)
            try:
                q.add(taskqueue.Task(name=name, payload=data, method='PULL', tag=token.queue_id()))
            except (taskqueue.TombstonedTaskError, taskqueue.TaskAlreadyExistsError):
                # Ignore publishing requests we've already decided to publish (multi-task concurrency)
                pass


def _should_post_event(auth_token, db_event):
    if auth_token.application == APP_FACEBOOK_WEEKLY:
        return False
    if auth_token.application == APP_TWITTER_DEV:
        return False
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
        invited = fb_events.get_all_members_count(db_event.fb_event)
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

    url = common.campaign_url(db_event.id, 'fb_event_wall')
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
            # Should only be one task
            if len(tasks) != 1:
                logging.error('Found too many tasks in our lease_tasks_by_tag: %s', len(tasks))
            task = tasks[0]
            posted = post_data_with_authtoken(task.payload, token)
            q.delete_tasks(task)

            # Only mark it up for delay, if we actually posted...
            if posted:
                next_post_time = datetime.datetime.now() + datetime.timedelta(seconds=token.time_between_posts)
                token = token.key.get()
                token.next_post_time = next_post_time
                token.put()


def post_data_with_authtoken(data, auth_token):
    try:
        if auth_token.application == APP_FACEBOOK_WEEKLY:
            city_name = data
            logging.info("  Posting weekly update for city: %s", city_name)
            # TODO: fix circular import
            from . import weekly
            return weekly.facebook_weekly_post(auth_token, city_name)
        else:
            event_id = data
            return post_event(auth_token, event_id)
    except Exception as e:
        logging.exception("Post Exception: %s", e)
        # Just in case there's something failing-after-posting,
        # we don't want to trigger rapid-fire posts in a loop.
        return True


def post_event(auth_token, event_id):
    logging.info("  Found event, posting %s", event_id)
    event_id = event_id
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if not db_event:
        logging.warning("Failed to post event: %s, dbevent deleted in dancedeets", event_id)
        return False
    if not db_event.has_content():
        logging.warning("Failed to post event: %s, due to %s", event_id, db_event.empty_reason)
        return False
    if (db_event.end_time or db_event.start_time) < datetime.datetime.now():
        logging.info('Not publishing %s because it is in the past.', db_event.id)
        return False
    return _post_event(auth_token, db_event)


def _post_event(auth_token, db_event):
    if auth_token.application == APP_TWITTER:
        twitter_event.twitter_post(auth_token, db_event)
    elif auth_token.application == APP_FACEBOOK:
        result = facebook_post(auth_token, db_event)
        if 'error' in result:
            if result.get('code') == 368 and result.get('error_subcode') == 1390008:
                next_post_time = datetime.datetime.now() + datetime.timedelta(days=1)
                auth_token = auth_token.key.get()
                auth_token.next_post_time = next_post_time
                auth_token.put()
                return False
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
    elif auth_token.application == APP_TWITTER_DEV:
        pass
    else:
        logging.error("Unknown application for OAuthToken: %s", auth_token.application)
        return False
    return True

class LookupGeoTarget(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, urlparams):
        return [
            ('search', cls.url('search', type='adgeolocation', **urlparams)),
        ]

    @classmethod
    def cache_key(cls, query, fetching_uid):
        return (fb_api.USERLESS_UID, json.dumps(query, sort_keys=True), 'OBJ_GEO_TARGET')

def facebook_post(auth_token, db_event):
    link = common.campaign_url(db_event.id, 'fb_feed')
    datetime_string = db_event.start_time.strftime('%s @ %s' % (common.DATE_FORMAT, common.TIME_FORMAT))

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
        # TODO: Can I @mention the people here too, like I do as a human? Or does it only work with pages?
        host = text.human_list('@[%s]' % x for x in page_admin_ids)

    # Tag it if we can
    if db_event.venue_id:
        venue = '@[%s]' % db_event.venue_id
    else:
        venue = db_event.location_name

    if not location:
        # Don't want to post events globally...too noisy
        return {}

    params = {
        'location': location,
        'date': human_date,
        'venue': venue,
    }
    messages = [
        'Dancers, are you ready? %(venue)s has an event on %(date)s in %(location)s.',
        'Hello %(location)s dancers, mark your calendars! We just found a new dance event on %(date)s at %(venue)s.',
        'Hey %(location)s dancers, save the date! Look what we found coming up on %(date)s at %(venue)s.',
        'Just posted! We have an upcoming dance event on %(date)s at %(venue)s in %(location)s.',
        'What\'s up %(location)s, there\'s a dance event at %(venue)s on %(date)s.',
    ]
    message = random.choice(messages) % params
    if host and host != venue:
        message += random.choice([
            ' Hosted by our friends at %(host)s.',
            ' Thanks to our buddies at %(host)s for hosting!',
            ' Hitup the awesome %(host)s with any questions you\'ve got!',
        ]) % {'host': host}
    if name:
        message += random.choice([
            ' Thanks to %(name)s for adding it to DanceDeets!',
            ' And a special thanks to %(name)s, for sharing it with you all on DanceDeets!',
            ' This event brought to you on DanceDeets courtesy of %(name)s!',
        ]) % {'name': name}
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
    venue_id = db_event.venue_id
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
            'location_types': 'city',
            'country_code': db_event.country,
            'q': city_state,
        }
        geo_target = fbl.get(LookupGeoTarget, geo_search, allow_cache=False)

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
        feed_targeting['cities'] = [{
            'key': city_key,
            #'radius': 80,
            #'distance_unit': 'kilometer',
        }]
    elif short_country:
        feed_targeting['countries'] = [short_country]
    full_targeting = {'geo_locations': feed_targeting}
    return full_targeting


APP_TWITTER = 'APP_TWITTER'
APP_TWITTER_DEV = 'APP_TWITTER_DEV' # disabled twitter dev
APP_FACEBOOK = 'APP_FACEBOOK'  # a butchering of OAuthToken!
APP_FACEBOOK_WALL = 'APP_FACEBOOK_WALL'  # a further butchering!
APP_FACEBOOK_WEEKLY = 'APP_FACEBOOK_WEEKLY' # weekly posts!

class OAuthToken(ndb.Model):
    user_id = ndb.StringProperty()
    token_nickname = ndb.StringProperty()
    application = ndb.StringProperty()
    temp_oauth_token = ndb.StringProperty()
    temp_oauth_token_secret = ndb.StringProperty()
    valid_token = ndb.BooleanProperty()
    oauth_token = ndb.StringProperty()
    oauth_token_secret = ndb.StringProperty()
    # Can we post the same thing multiple times (developer mode)
    allow_reposting = ndb.BooleanProperty()

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

class LookupUserAccounts(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('accounts', cls.url('%s/accounts' % object_id)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid or 'None', object_id, 'OBJ_USER_ACCOUNTS')


def get_dancedeets_fbl():
    page_id = '110312662362915'
    #page_id = '1375421172766829' # DD-Manager-Test
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
        all_page_ids = [x['id'] for x in all_pages]
        raise ValueError("Failed to find page id %s in user's page permissions: %s" % (page_uid, all_page_ids))
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
