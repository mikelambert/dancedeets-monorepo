#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp
import event
import search
import user

DEBUG = True

#TODO(lambert): send weekly emails with upcoming events per person
#TODO(lambert): send notifications to interested users when someone adds a new event?

#TODO(lambert): add a bunch of events to the db, then dump the db for saving it

URLS = [
    ('/events/view', event.MainHandler),
    ('/events/add', event.AddHandler),
    ('/events/search', search.SearchHandler),
    ('/user/edit', user.UserHandler),
]

def main():
     application = webapp.WSGIApplication(URLS, debug=DEBUG)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
