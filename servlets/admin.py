import collections
import json
import pprint
import time
import webapp2
from google.appengine.ext import db
import smemcache

import base_servlet
from events import eventdata
from events import users
import fb_api
from util import urls

class DeleteFBCacheHandler(webapp2.RequestHandler):
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
        access_token = None
        real_key = self.request.get('key')
        if not real_key:
            fb_uid = self.request.get('fb_uid')
            fbl = fb_api.FBLookup(fb_uid, access_token)
            fbtype_lookup = {
                'OBJ_PROFILE': fb_api.LookupProfile,
                'OBJ_USER': fb_api.LookupUser,
                'OBJ_USER_EVENTS': fb_api.LookupUserEvents,
                'OBJ_FRIEND_LIST': fb_api.LookupFriendList,
                'OBJ_EVENT': fb_api.LookupEvent,
                'OBJ_EVENT_MEMBERS': fb_api.LookupEventMembers,
                'OBJ_THING_FEED': fb_api.LookupThingFeed,
            }
            req_type = self.request.get('type')
            if req_type in fbtype_lookup:
                fbtype = fbtype_lookup[req_type]
            else:
                self.response.out.write('type %s  must be one of %s' % (req_type, fbtype_lookup.keys()))
                return
            key = fb_api.generate_key(fbtype, self.request.get('arg'))
            real_key = fbl.key_to_cache_key(key)
        memcache_result = smemcache.get(real_key)
        db_result = fb_api.FacebookCachedObject.get_by_key_name(real_key)
        self.response.out.write('Memcache:\n%s\n\n' % pprint.pformat(memcache_result, width=200))
        self.response.out.write('Database:\n%s\n\n' % pprint.pformat(db_result and db_result.decode_data() or None, width=200))
        self.response.out.write('MemcacheJSON:\n%s\n\n' % json.dumps(memcache_result))
        self.response.out.write('DatabaseJSON:\n%s\n\n' % json.dumps(db_result and db_result.decode_data() or None))

class ShowNoOwnerEventsHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        all_events = eventdata.DBEvent.query(eventdata.DBEvent.owner_fb_uid==None).fetch(1000)
        import logging
        logging.info("found %s events", len(all_events))
        for e in all_events:
            self.response.out.write('<a href="%s">%s</a><br>\n' % (urls.raw_fb_event_url(e.fb_event_id), e.fb_event_id))

class ShowUsersHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        num_fetch_users = int(self.request.get('num_users', 500))
        order_field = self.request.get('order_field', 'creation_time')
        all_users = users.User.all().order('-%s' % order_field).fetch(num_fetch_users)
        all_users = sorted(all_users, key=lambda x: getattr(x, order_field), reverse=True)
        client_counts = collections.defaultdict(lambda: 0)
        for user in all_users:
            for client in user.clients:
                client_counts[client] += 1
        user_ids = [x.fb_uid for x in all_users]
        fb_users = self.fbl.get_multi(fb_api.LookupUser, user_ids)

        self.display['client_counts'] = client_counts
        self.display['num_users'] = len(all_users)
        self.display['num_active_users'] = len([x for x in all_users if not x.expired_oauth_token])
        self.display['users'] = all_users
        self.display['fb_users'] = fb_users
        self.display['track_google_analytics'] = False
        self.render_template('show_users')

class ClearMemcacheHandler(webapp2.RequestHandler):
    def get(self):
        smemcache.flush_all()
        self.response.out.write("Flushed memcache!")


