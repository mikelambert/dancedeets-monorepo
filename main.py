#!/usr/bin/env python

import logging
import os
import webapp2
import yaml
from google.appengine.ext import ereporter
import base_servlet
from logic import event_auto_classifier
from servlets import about
from servlets import admin
from servlets import api
from servlets import calendar
from servlets import event
from servlets import feedback
from servlets import gprediction
from servlets import login
from servlets import myuser
from servlets import privacy
from servlets import profile_page
from servlets import search
from servlets import share
from servlets import source
from servlets import stats
from servlets import tasks
from servlets import tools
from servlets import youtube_simple_api
from util import batched_mapperworker

class DoNothingHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
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
    ('/tools/fb_data', admin.FBDataHandler),
    ('/tasks/load_events', tasks.LoadEventHandler),
    ('/tasks/load_users', tasks.LoadUserHandler),
    ('/tasks/load_event_attending', tasks.LoadEventAttendingHandler),
    ('/tasks/track_newuser_friends', tasks.TrackNewUserFriendsHandler),
    ('/tasks/reload_all_users', tasks.ReloadAllUsersHandler),
    ('/tasks/reload_all_events', tasks.ReloadAllEventsHandler),
    ('/tasks/reload_future_events', tasks.ReloadFutureEventsHandler),
    ('/tasks/reload_past_events', tasks.ReloadPastEventsHandler),
    ('/tasks/email_all_users', tasks.EmailAllUsersHandler),
    ('/tasks/email_user', tasks.EmailUserHandler),
    ('/tasks/load_all_potential_events', tasks.LoadAllPotentialEventsHandler),
    ('/tasks/load_potential_events_for_friends', tasks.LoadPotentialEventsForFriendsHandler),
    ('/tasks/load_potential_events_for_user', tasks.LoadPotentialEventsForUserHandler),
    ('/tasks/load_potential_events_from_wall_posts', tasks.LoadPotentialEventsFromWallPostsHandler),
    ('/tasks/compute_rankings', tasks.ComputeRankingsHandler),
    ('/tasks/memcache_future_events', tasks.MemcacheFutureEvents),
    ('/tasks/refresh_fulltext_search_index', tasks.RefreshFulltextSearchIndex),
    ('/tasks/timings_keep_alive', tasks.TimingsKeepAlive),
    ('/tasks/timings_process_day', tasks.TimingsProcessDay),
    ('/', search.RelevantHandler),
    ('/_ah/warmup', DoNothingHandler),
    ('/rankings', stats.RankingsHandler),
    ('/events/admin_nolocation_events', event.AdminNoLocationEventsHandler),
    ('/events/admin_potential_events', event.AdminPotentialEventViewHandler),
    ('/events/admin_edit', event.AdminEditHandler),
    ('/events/redirect', event.RedirectToEventHandler),
    ('/events/add', event.AddHandler),
    ('/events/feed', api.FeedHandler),
    ('/events/relevant', search.RelevantHandler),
    ('/events/rsvp_ajax', event.RsvpAjaxHandler),
    (r'/events/\d+/?', event.ShowEventHandler),
    ('/city/.*', search.CityHandler),
    ('/profile/[^/]*', profile_page.ProfileHandler),
    ('/profile/[^/]*/add_tag', profile_page.ProfileAddTagHandler),
    ('/youtube_simple_api', youtube_simple_api.YoutubeSimpleApiHandler),
    ('/calendar/feed', calendar.CalendarFeedHandler),
    ('/sources/admin_edit', source.AdminEditHandler),
    ('/user/edit', myuser.UserHandler),
    ('/login', login.LoginHandler),
    ('/share', share.ShareHandler),
    ('/about', about.AboutHandler),
    ('/privacy', privacy.PrivacyHandler),
    ('/help', feedback.HelpHandler),
    ('/feedback', feedback.FeedbackHandler),
    ('/mapreduce/worker_callback.*', batched_mapperworker.BatchedMapperWorkerCallbackHandler),
]

ereporter.register_logger()
prod_mode = 'SERVER_SOFTWARE' in os.environ and not os.environ['SERVER_SOFTWARE'].startswith('Dev')
if prod_mode:
    filename = 'facebook-prod.yaml'
else:
    filename = 'facebook.yaml'
base_servlet.FACEBOOK_CONFIG = yaml.load(file(filename, 'r'))

application = webapp2.WSGIApplication(URLS)
application.debug = True
application.prod_mode = prod_mode

