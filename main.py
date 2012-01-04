#!/usr/bin/env python

import logging
import os
import wsgiref.handlers
import yaml
from google.appengine.ext import webapp
from google.appengine.ext import ereporter
from google.appengine.ext.webapp.util import run_wsgi_app
import base_servlet
from servlets import about
from servlets import admin
from servlets import atom
from servlets import calendar
from servlets import city
from servlets import event
from servlets import feedback
from servlets import login
from servlets import myuser
from servlets import profile_page
from servlets import search
from servlets import share
from servlets import source
from servlets import stats
from servlets import tasks
from servlets import tools
from servlets import youtube_simple_api
import smemcache

class DoNothingHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
        return

URLS = [
    ('/tools/owned_events', tools.OwnedEventsHandler),
    ('/tools/unprocess_future_events', tools.UnprocessFutureEventsHandler),
    ('/tools/oneoff', tools.OneOffHandler),
    ('/tools/import_cities', tools.ImportCitiesHandler),
    ('/tools/migrate_dbevents', tools.MigrateDBEventsHandler),
    ('/tools/clear_memcache', admin.ClearMemcacheHandler),
    ('/tools/delete_fb_cache', admin.DeleteFBCacheHandler),
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
    ('/tasks/recache_search_index', tasks.RecacheSearchIndex),
    ('/', search.RelevantHandler),
    ('/_ah/warmup', DoNothingHandler),
    ('/rankings', stats.RankingsHandler),
    ('/events/admin_nolocation_events', event.AdminNoLocationEventsHandler),
    ('/events/admin_potential_events', event.AdminPotentialEventViewHandler),
    ('/events/admin_edit', event.AdminEditHandler),
    ('/events/redirect', event.RedirectToEventHandler),
    ('/events/view', event.ViewHandler),
    ('/events/add', event.AddHandler),
    ('/events/feed', atom.AtomHandler),
    ('/city/.*', city.CityHandler),
    ('/profile/[^/]*', profile_page.ProfileHandler),
    ('/profile/[^/]*/add_tag', profile_page.ProfileAddTagHandler),
    ('/youtube_simple_api', youtube_simple_api.YoutubeSimpleApiHandler),
    ('/calendar', calendar.CalendarHandler),
    ('/calendar/feed', calendar.CalendarFeedHandler),
    ('/sources/admin_edit', source.AdminEditHandler),
    ('/events/relevant', search.RelevantHandler),
    ('/events/rsvp_ajax', event.RsvpAjaxHandler),
    ('/user/edit', myuser.UserHandler),
    ('/login', login.LoginHandler),
    ('/share', share.ShareHandler),
    ('/about', about.AboutHandler),
    ('/help', feedback.HelpHandler),
    ('/feedback', feedback.FeedbackHandler),
]

class WebappHandlerAdapter(webapp.BaseHandlerAdapter):
    """An adapter to dispatch a ``webapp.RequestHandler``.

    Like in webapp, the handler is constructed, then ``initialize()`` is
    called, then the method corresponding to the HTTP request method is called.
    """

    def __call__(self, request, response):
        handler = self.handler()
        processed = handler.initialize(request, response)
        if not processed:
            method_name = _normalize_handler_method(request.method)
            method = getattr(handler, method_name, None)
            if not method:
                abort(501)

            # The handler only receives *args if no named variables are set.
            args, kwargs = request.route_args, request.route_kwargs
            if kwargs:
                args = ()

            try:
                method(*args, **kwargs)
            except Exception, e:
                handler.handle_exception(e, request.app.debug)

webapp.WebappHandlerAdapter = WebappHandlerAdapter #HACK

ereporter.register_logger()
prod_mode = not os.environ['SERVER_SOFTWARE'].startswith('Dev')
if prod_mode:
    filename = 'facebook-prod.yaml'
else:
    filename = 'facebook.yaml'
base_servlet.FACEBOOK_CONFIG = yaml.load(file(filename, 'r'))

application = webapp.WSGIApplication(URLS)
application.debug = True
application.prod_mode = prod_mode

