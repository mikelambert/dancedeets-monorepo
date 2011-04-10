import logging
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
from logic import potential_events

class UnprocessFutureEvents(Mapper):
    KIND = fb_api.FacebookCachedObject

    def map(self, entity):
        if entity.key().name().endswith('OBJ_EVENT'):
            if entity.json_data:
                event = entity.decode_data()
                if not event['deleted']:
                    info = event['info']
                    if info['start_time'] > '2011-04-05' and info['updated_time'] > '2011-04-05':
                        if event_classifier.is_dance_event(event):
                            pe = potential_events.PotentialEvent.get_or_insert(str(event['info']['id']))
                            pe.looked_at = False
                            pe.put()
                            logging.info("PE %s", event['info']['id'])
        return ([], [])

class UnprocessFutureEventsHandler(webapp.RequestHandler):
    def get(self):
        m = UnprocessFutureEvents()
        m.run()
        return

class OneOffHandler(webapp.RequestHandler):
    def get(self):
        return

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


