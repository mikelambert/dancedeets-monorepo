import time
from google.appengine.ext import db
from google.appengine.ext import webapp

from google.appengine.ext import deferred
from util.mapper import Mapper
from events import eventdata

class MyModelMapper(Mapper):
    KIND = eventdata.DBEvent

    def map(self, entity):
        if entity.key().name():
            return ([], [])

        new_entity = eventdata.DBEvent(
            key_name = str(entity.__dict__['_entity']['fb_event_id']),
            tags = entity.tags,
            creating_fb_uid = entity.creating_fb_uid,
        )

        return ([new_entity], [entity])

class MigrateDBEventsHandler(webapp.RequestHandler):
    def get(self):
        m = MyModelMapper()
        m.run()
        #deferred.defer(m.run)
        self.response.out.write('yay!')

class ClearMemcacheHandler(webapp.RequestHandler):
    def get(self):
        smemcache.flush_all()
        self.response.out.write("Flushed memcache!")


