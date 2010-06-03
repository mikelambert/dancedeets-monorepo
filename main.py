#!/usr/bin/env python

import os
import wsgiref.handlers
from google.appengine.ext import webapp
import base_servlet
import event
import search
import login
import myuser
import tasks
import yaml


DEBUG = True

#TODO(lambert): dump the db for importing into the local store. need good test data.
# http://code.google.com/appengine/docs/python/tools/uploadingdata.html

#TODO(lambert): setup webtest to test the wsgi app as a regression test to ensure everything is working
# http://pythonpaste.org/webtest/

#TODO(lambert): set up fine-grained event recording for performance monitoring
# http://code.google.com/appengine/docs/python/tools/appstats.html

URLS = [
    ('/tasks/load_events', tasks.LoadEventHandler),
    ('/tasks/load_users', tasks.LoadUserHandler),
    ('/tasks/track_newuser_friends', tasks.TrackNewUserFriendsHandler),
    ('/events/view', event.ViewHandler),
    ('/events/add', event.AddHandler),
    ('/events/search', search.SearchHandler),
    ('/events/rsvp_ajax', event.RsvpAjaxHandler),
    ('/user/edit', myuser.UserHandler),
    ('/login', login.LoginHandler),
]

def main():
    DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
    if DEBUG:
        filename = 'facebook.yaml'
    else:
        filename = 'facebook-prod.yaml'
    base_servlet.FACEBOOK_CONFIG = yaml.load(file(filename, 'r'))
     application = webapp.WSGIApplication(URLS, debug=DEBUG)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
