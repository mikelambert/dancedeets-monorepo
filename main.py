#!/usr/bin/env python

import logging
import os
import wsgiref.handlers
import yaml
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import base_servlet
from servlets import admin
from servlets import event
from servlets import search
from servlets import login
from servlets import myuser
from servlets import tasks
from servlets import tools
import smemcache


DEBUG = True

#TODO(lambert): setup webtest to test the wsgi app as a regression test to ensure everything is working
# http://pythonpaste.org/webtest/

URLS = [
    ('/tools/migrate_dbevents', tools.MigrateDBEventsHandler),
    ('/tasks/cleanup_work', tasks.CleanupWorkHandler),
    ('/tasks/load_events', tasks.LoadEventHandler),
    ('/tasks/load_users', tasks.LoadUserHandler),
    ('/tasks/load_event_members', tasks.LoadEventMembersHandler),
    ('/tasks/track_newuser_friends', tasks.TrackNewUserFriendsHandler),
    ('/tasks/reload_all_users', tasks.ReloadAllUsersHandler),
    ('/tasks/reload_future_events', tasks.ReloadFutureEventsHandler),
    ('/tasks/reload_past_events', tasks.ReloadPastEventsHandler),
    ('/tasks/resave_all_events', tasks.ResaveAllEventsHandler),
    ('/tasks/email_all_users', tasks.EmailAllUsersHandler),
    ('/tasks/email_user', tasks.EmailUserHandler),
    ('/', search.RelevantHandler),
    ('/events/admin_edit', event.AdminEditHandler),
    ('/events/view', event.ViewHandler),
    ('/events/add', event.AddHandler),
    ('/events/search', search.SearchHandler),
    ('/events/results', search.ResultsHandler),
    ('/events/relevant', search.RelevantHandler),
    ('/events/rsvp_ajax', event.RsvpAjaxHandler),
    ('/user/edit', myuser.UserHandler),
    ('/login', login.LoginHandler),
    ('/admin/clear_memcache', admin.ClearMemcacheHandler),
    ('/admin/delete_fb_cache', admin.DeleteFBCacheHandler),
]

class MyWSGIApplication(webapp.WSGIApplication):
    def __call__(self, environ, start_response):
        """Called by WSGI when a request comes in."""
        request = self.REQUEST_CLASS(environ)
        response = self.RESPONSE_CLASS()

        webapp.WSGIApplication.active_instance = self

        processed = False
        handler = None
        groups = ()
        for regexp, handler_class in self._url_mapping:
            match = regexp.match(request.path)
            if match:
                handler = handler_class()
                processed = handler.initialize(request, response)
                groups = match.groups()
                break

        self.current_request_args = groups

        if not processed:
            if handler:
                try:
                    method = environ['REQUEST_METHOD']
                    if method == 'GET':
                        handler.get(*groups)
                    elif method == 'POST':
                        handler.post(*groups)
                    elif method == 'HEAD':
                        handler.head(*groups)
                    elif method == 'OPTIONS':
                        handler.options(*groups)
                    elif method == 'PUT':
                        handler.put(*groups)
                    elif method == 'DELETE':
                        handler.delete(*groups)
                    elif method == 'TRACE':
                        handler.trace(*groups)
                    else:
                        handler.error(501)
                except Exception, e:
                    handler.handle_exception(e, DEBUG)
            else:
                response.set_status(404)

        response.wsgi_write(start_response)
        return ['']

def main():
    DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
    if DEBUG:
        filename = 'facebook.yaml'
    else:
        filename = 'facebook-prod.yaml'
    base_servlet.FACEBOOK_CONFIG = yaml.load(file(filename, 'r'))
     application = MyWSGIApplication(URLS, debug=DEBUG)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
