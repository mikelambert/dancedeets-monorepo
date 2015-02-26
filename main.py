#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import logging
logging.info("Begin modules")
import webapp2
from google.appengine.ext import ereporter
from google.appengine.ext.ndb import tasklets

# We call this here to force loading _strptime module upfront,
# because once threads come online and call strptime(), they try to load _strptime lazily,
# and the second thread to call it while the first one is loading with the lock, triggers an exception.
# More info:
# http://bugs.python.org/issue7980
# http://code-trick.com/python-bug-attribute-error-_strptime/
import _strptime


prod_mode = 'SERVER_SOFTWARE' in os.environ and not os.environ['SERVER_SOFTWARE'].startswith('Dev')

# Make python-twitter work in the sandbox (not yet sure about prod...)
if not prod_mode:
    from google.appengine.tools.devappserver2.python import sandbox
    sandbox._WHITE_LIST_C_MODULES += ['_ssl']

logging.info("Begin servlets")
import base_servlet
from event_scraper import source_servlets
from search import search_servlets
from search import search_tasks
from servlets import about
from servlets import admin
from servlets import api
from servlets import calendar
from servlets import event
from servlets import event_proxy
from servlets import feedback
from servlets import home
from servlets import gprediction
from servlets import login
from servlets import mobile_apps
from servlets import myuser
from servlets import privacy
from servlets import profile_page
from servlets import pubsub_setup
from servlets import share
from servlets import stats
from servlets import tasks
from servlets import tools
from servlets import youtube_simple_api
from topics import topic_servlets

from util import batched_mapperworker

logging.info("Finished modules")

class DoNothingHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
        from nlp import event_auto_classifier
        logging.info("Loading regexes")
        event_auto_classifier.build_regexes()
        logging.info("Loaded regexes")
        return

URLS = [
    ('/tools/download_training_data/([^/]+)?', gprediction.DownloadTrainingDataHandler),
    ('/tools/generate_training_data', gprediction.GenerateTrainingDataHandler),
    ('/tools/owned_events', tools.OwnedEventsHandler),
    ('/tools/unprocess_future_events', tools.UnprocessFutureEventsHandler),
    ('/tools/auto_add_potential_events', tools.AutoAddPotentialEventsHandler),
    ('/tools/oneoff', tools.OneOffHandler),
    ('/tools/import_cities', tools.ImportCitiesHandler),
    ('/tools/clear_memcache', admin.ClearMemcacheHandler),
    ('/tools/delete_fb_cache', admin.DeleteFBCacheHandler),
    ('/tools/show_noowner_events', admin.ShowNoOwnerEventsHandler),
    ('/tools/show_users', admin.ShowUsersHandler),
    ('/tools/export_sources', tools.ExportSourcesHandler),
    ('/tools/fb_data', admin.FBDataHandler),
    ('/tools/facebook_post', pubsub_setup.FacebookPostHandler),
    ('/tasks/load_events', tasks.LoadEventHandler),
    ('/tasks/load_users', tasks.LoadUserHandler),
    ('/tasks/load_event_attending', tasks.LoadEventAttendingHandler),
    ('/tasks/track_newuser_friends', tasks.TrackNewUserFriendsHandler),
    ('/tasks/reload_all_users', tasks.ReloadAllUsersHandler),
    ('/tasks/reload_all_events', tasks.ReloadAllEventsHandler),
    ('/tasks/reload_future_events', tasks.ReloadFutureEventsHandler),
    ('/tasks/reload_past_events', tasks.ReloadPastEventsHandler),
    ('/tasks/email_all_users', search_tasks.EmailAllUsersHandler),
    ('/tasks/email_user', search_tasks.EmailUserHandler),
    ('/tasks/load_all_potential_events', tasks.LoadAllPotentialEventsHandler),
    ('/tasks/load_potential_events_for_friends', tasks.LoadPotentialEventsForFriendsHandler),
    ('/tasks/load_potential_events_for_user', tasks.LoadPotentialEventsForUserHandler),
    ('/tasks/load_potential_events_from_wall_posts', tasks.LoadPotentialEventsFromWallPostsHandler),
    ('/tasks/compute_rankings', tasks.ComputeRankingsHandler),
    ('/tasks/memcache_future_events', search_tasks.MemcacheFutureEvents),
    ('/tasks/refresh_fulltext_search_index', search_tasks.RefreshFulltextSearchIndex),
    ('/tasks/timings_keep_alive', tasks.TimingsKeepAlive),
    ('/tasks/timings_process_day', tasks.TimingsProcessDay),
    ('/', search_servlets.RelevantHandler),
    ('/_ah/warmup', DoNothingHandler),
    ('/rankings', stats.RankingsHandler),
    ('/events/admin_nolocation_events', event.AdminNoLocationEventsHandler),
    ('/events/admin_potential_events', event.AdminPotentialEventViewHandler),
    ('/events/admin_edit', event.AdminEditHandler),
    ('/events/redirect', event.RedirectToEventHandler),
    ('/events_add', event.AddHandler),
    ('/events/relevant', search_servlets.RelevantHandler),
    ('/events/rsvp_ajax', event.RsvpAjaxHandler),
    ('/events/image_proxy/(\d+)', event_proxy.ImageProxyHandler),
    (r'/events/\d+/?', event.ShowEventHandler),
    ('/city/.*', search_servlets.CityHandler),
    ('/profile/[^/]*', profile_page.ProfileHandler),
    ('/profile/[^/]*/add_tag', profile_page.ProfileAddTagHandler),
    ('/youtube_simple_api', youtube_simple_api.YoutubeSimpleApiHandler),
    ('/calendar/feed', calendar.CalendarFeedHandler),
    ('/sources/admin_edit', source_servlets.AdminEditHandler),
    ('/user/edit', myuser.UserHandler),
    ('/login', login.LoginHandler),
    ('/mobile_apps', mobile_apps.MobileAppsHandler),
    ('/share', share.ShareHandler),
    ('/about', about.AboutHandler),
    ('/privacy', privacy.PrivacyHandler),
    ('/help', feedback.HelpHandler),
    ('/feedback', feedback.FeedbackHandler),
    ('/mapreduce/worker_callback.*', batched_mapperworker.BatchedMapperWorkerCallbackHandler),
    ('/home', home.HomeHandler),

    ('/topic/?', topic_servlets.TopicListHandler),
    ('/topic/([^/]+)/?', topic_servlets.TopicHandler),
    ('/topic_add', topic_servlets.AdminAddTopicHandler),
    ('/twitter/oauth_start', pubsub_setup.TwitterOAuthStartHandler),
    ('/twitter/oauth_callback', pubsub_setup.TwitterOAuthCallbackHandler),
    ('/twitter/oauth_success', pubsub_setup.TwitterOAuthSuccessHandler),
    ('/twitter/oauth_failure', pubsub_setup.TwitterOAuthFailureHandler),
    ('/facebook/page_start', pubsub_setup.FacebookPageSetupHandler),
    ('/tasks/social_publisher', tasks.SocialPublisherHandler),
    ('/tasks/post_japan_events', tasks.PostJapanEventsHandler),

    ('/api/v1.0/events/\d+/?', api.EventHandler),
    ('/api/v(\d+).(\d+)/search', api.SearchHandler),
    ('/api/v1.0/auth', api.AuthHandler),
]

if prod_mode:
    ereporter.register_logger()
application = webapp2.WSGIApplication(URLS)
application.debug = True
application.prod_mode = prod_mode

