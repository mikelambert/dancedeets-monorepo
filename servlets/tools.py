import logging
import time
import webapp2
from google.appengine.ext import db
from google.appengine.ext import deferred

from mapreduce import context
from mapreduce import control
from mapreduce import operation as op
from mapreduce import util

from events import cities
from events import eventdata
from events import users
import fb_api
from logic import auto_add
from logic import event_classifier
from logic import mr_dump
from logic import mr_prediction
from logic import potential_events
from logic import thing_db
from servlets import tasks


class UnprocessFutureEventsHandler(webapp2.RequestHandler):
    def get(self):
        #TODO(lambert): reimplement if needed:
        #if entity.key().name().endswith('OBJ_EVENT'):
        #    if entity.json_data:
        #        event = entity.decode_data()
        #        if not event['empty']:
        #            info = event['info']
        #            if info.get('start_time') > '2011-04-05' and info['updated_time'] > '2011-04-05':
        #                pe = potential_events.PotentialEvent.get_or_insert(str(event['info']['id']))
        #                pe.looked_at = None
        #                pe.put()
        #                logging.info("PE %s", event['info']['id'])
        return

def map_delete_cached_with_wrong_user_id(fbo):
    user_id, obj_id, obj_type = fbo.key().name().split('.')
    bl = fb_api.BatchLookup
    bl_types = (bl.OBJECT_EVENT, bl.OBJECT_EVENT_ATTENDING, bl.OBJECT_EVENT_MEMBERS, bl.OBJECT_THING_FEED, bl.OBJECT_VENUE)
    if obj_type in bl_types and user_id != '701004':
        yield op.db.Delete(fbo)


class OneOffHandler(tasks.BaseTaskFacebookRequestHandler):#webapp2.RequestHandler):
    def get(self):
        mr_dump.mr_dump_events(self.batch_lookup)

class AutoAddPotentialEventsHandler(tasks.BaseTaskFacebookRequestHandler):
    def get(self):
        auto_add.mr_classify_potential_events(self.batch_lookup)

class OwnedEventsHandler(webapp2.RequestHandler):
    def get(self):
        db_events_query = eventdata.DBEvent.gql('WHERE owner_fb_uid = :1', self.request.get('owner_id'))
        db_events = db_events_query.fetch(1000)

        batch_lookup = fb_api.CommonBatchLookup(None, None)

        print 'Content-type: text/plain\n\n'
        fb_events = fb_api.FacebookCachedObject.get_by_key_name(batch_lookup._string_key(batch_lookup._event_key(x.fb_event_id)) for x in db_events)
        for db_event, fb_event in zip(db_events, fb_events):
            real_fb_event = fb_event.decode_data()
            print db_event.tags, real_fb_event['info']['name']

class ImportCitiesHandler(webapp2.RequestHandler):
    def get(self):
        cities.import_cities()
        self.response.out.write("Imported Cities!")

class ClearMemcacheHandler(webapp2.RequestHandler):
    def get(self):
        smemcache.flush_all()
        self.response.out.write("Flushed memcache!")


