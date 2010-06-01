#!/usr/bin/env python

import os
import wsgiref.handlers
from google.appengine.ext import webapp
import event
import search
import login
import myuser
from facebook import webappfb
import tasks
import yaml


DEBUG = True

#TODO(lambert): add a bunch of events to the db, then dump the db for saving it

URLS = [
    ('/tasks/load_events', tasks.LoadEventHandler),
    ('/tasks/load_users', tasks.LoadUserHandler),
    ('/events/view', event.ViewHandler),
    ('/events/add', event.AddHandler),
    ('/events/search', search.SearchHandler),
    ('/events/rsvp_ajax', event.RsvpAjaxHandler),
    ('/user/edit', myuser.UserHandler),
    ('/login', login.LoginHandler),
]

def main():
    DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
    if not DEBUG:
        webappfb.FACEBOOK_CONFIG = yaml.load(file('facebook-prod.yaml', 'r'))
     application = webapp.WSGIApplication(URLS, debug=DEBUG)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
