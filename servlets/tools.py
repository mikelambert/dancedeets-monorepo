import time
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext import deferred

from util.mapper import Mapper
from events import cities
from events import eventdata
from events import users
import fb_api
from logic import event_classifier

class MyModelMapper(Mapper):
    KIND = fb_api.FacebookCachedObject

    def map(self, entity):
        if 'OBJ_USER' in entity.key().name() or '701004' in entity.key().name():
            return ([], [])
        return ([], [entity])

class OneOffHandler(webapp.RequestHandler):
    def get(self):
        m = MyModelMapper()
        m.run()
        self.response.out.write('yay!')

class ImportCitiesHandler(webapp.RequestHandler):
    def get(self):
        cities.import_cities()
        self.response.out.write("Imported Cities!")


class DBEventMapper(Mapper):
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
        m = DBEventMapper()
        m.run()
        #deferred.defer(m.run)
        self.response.out.write('Trigger DBEvent Migration Mapreduce!')

class ClearMemcacheHandler(webapp.RequestHandler):
    def get(self):
        smemcache.flush_all()
        self.response.out.write("Flushed memcache!")


