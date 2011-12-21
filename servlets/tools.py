import csv
import logging
import StringIO
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
from logic import thing_db

class UnprocessFutureEvents(Mapper):
    KIND = fb_api.FacebookCachedObject

    def map(self, entity):
        if entity.key().name().endswith('OBJ_EVENT'):
            if entity.json_data:
                event = entity.decode_data()
                if not event['deleted']:
                    info = event['info']
                    if info.get('start_time') > '2011-04-05' and info['updated_time'] > '2011-04-05':
                        if event_classifier.is_dance_event(event):
                            pe = potential_events.PotentialEvent.get_or_insert(str(event['info']['id']))
                            pe.looked_at = None
                            pe.put()
                            logging.info("PE %s", event['info']['id'])
        return ([], [])

class UnprocessFutureEventsHandler(webapp.RequestHandler):
    def get(self):
        m = UnprocessFutureEvents()
        m.run()
        return

from servlets import tasks
from logic import unique_attendees
class OneOffHandler(tasks.BaseTaskFacebookRequestHandler):#webapp.RequestHandler):
    def get(self):
        mrp = unique_attendees.mr_count_attendees_per_city(self.batch_lookup)
        self.response.out.write("pipeline id is " + mrp.pipeline_id)

class OwnedEventsHandler(webapp.RequestHandler):
    def get(self):
        db_events_query = eventdata.DBEvent.gql('WHERE owner_fb_uid = :1', self.request.get('owner_id'))
        db_events = db_events_query.fetch(1000)

        batch_lookup = fb_api.CommonBatchLookup(None, None)

        print 'Content-type: text/plain\n\n'
        fb_events = fb_api.FacebookCachedObject.get_by_key_name(batch_lookup._string_key(batch_lookup._event_key(x.fb_event_id)) for x in db_events)
        for db_event, fb_event in zip(db_events, fb_events):
            real_fb_event = fb_event.decode_data()
            print db_event.tags, real_fb_event['info']['name']

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
        #m.run()

class ClearMemcacheHandler(webapp.RequestHandler):
    def get(self):
        smemcache.flush_all()
        self.response.out.write("Flushed memcache!")


