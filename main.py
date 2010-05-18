#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp
import event
import search
import user

DEBUG = True

#TODO(lambert): add a bunch of events to the db, then dump the db for saving it

URLS = [
    ('/events/view', event.ViewHandler),
    ('/events/add', event.AddHandler),
    ('/events/search', search.SearchHandler),
    ('/events/rsvp_ajax', event.RsvpAjaxHandler),
    ('/user/edit', user.UserHandler),
]

def main():
     application = webapp.WSGIApplication(URLS, debug=DEBUG)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
