# -*-*- encoding: utf-8 -*-*-

import datetime
import logging
import re
import time

from google.appengine.ext import ndb

from events import eventdata
from util import fb_events
from util import taskqueue
from .twitter import event as facebook_event
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
        return _should_queue_event_for_posting(auth_token, db_event)
    return _eventually_publish_data(event_id, should_post, token_nickname)

def eventually_publish_city_key(city_key):
    print city_key
    def should_post(auth_token):
        return auth_token.application == APP_FACEBOOK_WEEKLY
    return _eventually_publish_data(city_key, should_post)

def _eventually_publish_data(data, should_post, token_nickname=None):
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

def _should_queue_event_for_posting(auth_token, db_event):
    func = POSTING_FILTERS.get(auth_token.application)
    result = func(auth_token, db_event)
    if result:
        logging.info("Publishing event %s", db_event.id)
    return True

def _should_post_event_to_account(auth_token, db_event):
    geocode = db_event.get_geocode()
    if not geocode:
        # Don't post events without a location. It's too confusing...
        return False
    event_country = geocode.country()
    if auth_token.country_filters and event_country not in auth_token.country_filters:
        logging.info("Skipping event due to country filters")
        return False
    return True

def _should_post_on_event_wall(auth_token, db_event):
    if not _should_post_event_to_account(auth_token, db_event):
        return False
    # Additional filtering for FB Wall postings, since they are heavily-rate-limited by FB.
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
            posted = _post_data_with_authtoken(task.payload, token)
            q.delete_tasks(task)

            # Only mark it up for delay, if we actually posted...
            if posted:
                next_post_time = datetime.datetime.now() + datetime.timedelta(seconds=token.time_between_posts)
                token = token.key.get()
                token.next_post_time = next_post_time
                token.put()


def _post_data_with_authtoken(data, auth_token):
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
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if _should_still_post_about_event(auth_token, db_event):
        return _post_event(auth_token, db_event)
    else:
        return False

def _should_still_post_about_event(auth_token, db_event):
    if not db_event:
        logging.warning("Failed to post event: %s, dbevent deleted in dancedeets", db_event)
        return False
    if not db_event.has_content():
        logging.warning("Failed to post event: %s, due to %s", db_event.id, db_event.empty_reason)
        return False
    if (db_event.end_time or db_event.start_time) < datetime.datetime.now():
        logging.info('Not publishing %s because it is in the past.', db_event.id)
        return False
    return True

def _post_event(auth_token, db_event):
    if auth_token.application == APP_TWITTER:
        twitter_event.twitter_post(auth_token, db_event)
    elif auth_token.application == APP_FACEBOOK:
        result = facebook_event.facebook_post(auth_token, db_event)
        if 'error' in result:
            if result.get('code') == 368 and result.get('error_subcode') == 1390008:
                logging.error('We are posting too fast to the facebook wall, so wait a day and try again later')
                next_post_time = datetime.datetime.now() + datetime.timedelta(days=1)
                auth_token = auth_token.key.get()
                auth_token.next_post_time = next_post_time
                # And space things out a tiny bit more!
                auth_token.time_between_posts += 1
                auth_token.put()
                return False
            logging.error("Facebook Post Error: %r", result)
        else:
            logging.info("Facebook result was %r", result)
    elif auth_token.application == APP_FACEBOOK_WALL:
        result = facebook_event.post_on_event_wall(db_event)
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

POSTING_FILTERS = {
    APP_FACEBOOK: _should_post_event_to_account,
    APP_TWITTER: _should_post_event_to_account,
    APP_FACEBOOK_WALL: _should_post_on_event_wall,
}
