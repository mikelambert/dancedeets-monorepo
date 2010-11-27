import time
from google.appengine.ext import db
from google.appengine.ext import webapp
import smemcache

import base_servlet
from events import users

class DeleteFBCacheHandler(webapp.RequestHandler):
        def get(self):
                self.response.headers['Content-Type'] = 'text/plain'
                try:
                        while True:
                                q = db.GqlQuery("SELECT __key__ FROM FacebookCachedObject")
                                if not q.count():
                                    break
                                db.delete(q.fetch(200))
                                time.sleep(0.1)
                except Exception, e:
                        self.response.out.write(repr(e)+'\n')
                        pass

class ShowUsersHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
        all_users = users.User.gql('order by creation_time').fetch(1000)
        self.display['num_users'] = len(all_users)
        self.display['users'] = all_users
        self.render_template('show_users')

class ClearMemcacheHandler(webapp.RequestHandler):
    def get(self):
        smemcache.flush_all()
        self.response.out.write("Flushed memcache!")


