import pprint
import time
from google.appengine.ext import db
from google.appengine.ext import webapp
from django.utils import simplejson
import smemcache

import base_servlet
from events import eventdata
from events import users
import fb_api
from util import urls

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

class FBDataHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        fb_graph = None
        real_key = self.request.get('key')
        if not real_key:
            fb_uid = self.request.get('fb_uid')
            batch_lookup = fb_api.CommonBatchLookup(fb_uid, fb_graph)
            fbtype = self.request.get('type')
            if fbtype == batch_lookup.OBJECT_PROFILE:
                key = batch_lookup._profile_key(self.request.get('arg'))
            elif fbtype == batch_lookup.OBJECT_USER:
                key = batch_lookup._user_key(self.request.get('arg'))
            elif fbtype == batch_lookup.OBJECT_USER_EVENTS:
                key = batch_lookup._user_events_key(self.request.get('arg'))
            elif fbtype == batch_lookup.OBJECT_FRIEND_LIST:
                key = batch_lookup._friend_list_key(self.request.get('arg'))
            elif fbtype == batch_lookup.OBJECT_EVENT:
                key = batch_lookup._event_key(self.request.get('arg'))
            elif fbtype == batch_lookup.OBJECT_EVENT_MEMBERS:
                key = batch_lookup._event_members_key(self.request.get('arg'))
            elif fbtype == batch_lookup.OBJECT_FQL:
                key = batch_lookup._fql_key(self.request.get('arg'))
            else:
                self.response.out.write('type must be one of BatchLookup.OBJECT_*: %s' % fbtype)
                return
            real_key = batch_lookup._string_key(key)
        memcache_result = smemcache.get(real_key)
        db_result = fb_api.FacebookCachedObject.get_by_key_name(real_key)
        self.response.out.write('Memcache:\n%s\n\n' % pprint.pformat(memcache_result, width=200))
        self.response.out.write('Database:\n%s\n\n' % pprint.pformat(db_result and db_result.decode_data() or None, width=200))
        self.response.out.write('MemcacheJSON:\n%s\n\n' % simplejson.dumps(memcache_result))
        self.response.out.write('DatabaseJSON:\n%s\n\n' % simplejson.dumps(db_result and db_result.decode_data() or None))

class ShowNoOwnerEventsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        all_events = eventdata.DBEvent.gql('WHERE owner_fb_uid = :1', None).fetch(1000)
        import logging
        logging.info("found %s events", len(all_events))
        for e in all_events:
            self.response.out.write('<a href="%s">%s</a><br>\n' % (urls.raw_fb_event_url(e.fb_event_id), e.fb_event_id))

class ShowUsersHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        all_users = users.User.all().fetch(1000)
        all_users = reversed(sorted(all_users, key=lambda x: x.creation_time))
        self.display['num_users'] = len(all_users)
        self.display['users'] = all_users
        self.display['track_google_analytics'] = False
        self.render_template('show_users')

class ClearMemcacheHandler(webapp.RequestHandler):
    def get(self):
        smemcache.flush_all()
        self.response.out.write("Flushed memcache!")


